import os
import sys
import io
import base64
from urllib.parse import urlencode

# Add backend directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app

def handler(event, context):
    """
    AWS Lambda / Netlify Serverless Function WSGI Adapter for Flask
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "/")
    query_params = event.get("queryStringParameters") or {}
    query_string = urlencode(query_params)
    headers = event.get("headers") or {}
    
    body = event.get("body") or ""
    if event.get("isBase64Encoded", False):
        body_bytes = base64.b64decode(body)
    else:
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body

    environ = {
        "REQUEST_METHOD": http_method,
        "SCRIPT_NAME": "",
        "PATH_INFO": path,
        "QUERY_STRING": query_string,
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "443",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": io.BytesIO(body_bytes),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "CONTENT_LENGTH": str(len(body_bytes)),
        "CONTENT_TYPE": headers.get("content-type", headers.get("Content-Type", "")),
    }

    for key, value in headers.items():
        environ_key = "HTTP_" + key.upper().replace("-", "_")
        environ[environ_key] = value

    response_headers = []
    response_status = ["200 OK"]

    def start_response(status, response_headers_list, exc_info=None):
        response_status[0] = status
        response_headers.extend(response_headers_list)
        return lambda data: None

    response_iter = app(environ, start_response)
    response_body = b"".join(response_iter)

    status_code = int(response_status[0].split(" ")[0])
    
    header_dict = {}
    for k, v in response_headers:
        header_dict[k] = v

    is_binary = not any(
        ct in header_dict.get("Content-Type", "").lower()
        for ct in ["text/", "application/json", "application/javascript", "application/xml"]
    )

    if is_binary:
        encoded_body = base64.b64encode(response_body).decode("utf-8")
        is_b64 = True
    else:
        try:
            encoded_body = response_body.decode("utf-8")
            is_b64 = False
        except UnicodeDecodeError:
            encoded_body = base64.b64encode(response_body).decode("utf-8")
            is_b64 = True

    return {
        "statusCode": status_code,
        "headers": header_dict,
        "body": encoded_body,
        "isBase64Encoded": is_b64
    }

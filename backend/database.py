import os
import sys
import mysql.connector

# Ensure UTF-8 stdout/stderr to prevent UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "nutriscan"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

try:
    db = get_db()
    print("[NutriScan] MySQL Database Connected successfully.")
    db.close()
except Exception as e:
    print(f"[NutriScan] Database connection notice: {e}")
import os
import mysql.connector

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
    print("✅ NutriScan MySQL Database Connected!")
    db.close()
except Exception as e:
    print("❌ Database connection failed:", e)
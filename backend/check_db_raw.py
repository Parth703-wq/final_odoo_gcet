
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys

# Add current directory to path to import app
sys.path.append(os.getcwd())

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "rental_management_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def check_raw():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, product_name FROM invoice_items WHERE invoice_id = 7"))
        items = res.fetchall()
        print(f"RAW SQL ITEM COUNT for Invoice 7: {len(items)}")
        for item in items:
            print(f"ID: {item[0]}, Name: {item[1]}")

if __name__ == "__main__":
    check_raw()

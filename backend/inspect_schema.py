
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sys

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "rental_management_db")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def inspect_schema():
    with engine.connect() as conn:
        print("--- Invoices Table ---")
        res = conn.execute(text("DESCRIBE invoices"))
        for row in res:
            print(f"{row[0]}: {row[1]}")
            
        print("\n--- Invoice Items Table ---")
        res = conn.execute(text("DESCRIBE invoice_items"))
        for row in res:
            print(f"{row[0]}: {row[1]}")

if __name__ == "__main__":
    inspect_schema()

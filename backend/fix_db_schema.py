
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

def update_schema():
    with engine.connect() as conn:
        print("Updating 'invoices' table...")
        
        # Add missing columns to invoices
        columns_to_add = [
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS rental_start_date DATETIME null",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS rental_end_date DATETIME null",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS cgst FLOAT DEFAULT 0.0",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS sgst FLOAT DEFAULT 0.0",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS igst FLOAT DEFAULT 0.0",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS vendor_company_name VARCHAR(255) null",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS vendor_gstin VARCHAR(15) null",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_name VARCHAR(255) null",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS customer_gstin VARCHAR(15) null",
            "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS vendor_logo VARCHAR(500) null"
        ]
        
        for sql in columns_to_add:
            try:
                conn.execute(text(sql))
                print(f"✓ Executed: {sql[:50]}...")
            except Exception as e:
                print(f"! Error: {e}")
        
        print("\nUpdating 'invoice_items' table...")
        item_columns = [
            "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS cgst FLOAT DEFAULT 0.0",
            "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS sgst FLOAT DEFAULT 0.0",
            "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS igst FLOAT DEFAULT 0.0"
        ]
        for sql in item_columns:
            try:
                conn.execute(text(sql))
                print(f"✓ Executed: {sql[:50]}...")
            except Exception as e:
                print(f"! Error: {e}")
        
        conn.commit()
    print("\nSchema update complete!")

if __name__ == "__main__":
    update_schema()

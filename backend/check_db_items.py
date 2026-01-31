
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
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
SessionLocal = sessionmaker(bind=engine)

from app.models.invoice import Invoice, InvoiceItem

def check():
    db = SessionLocal()
    try:
        inv_id = 7
        invoice = db.query(Invoice).filter(Invoice.id == inv_id).first()
        if not invoice:
            print(f"FAILED: Invoice {inv_id} not found in DB {DB_NAME}")
            return
        
        print(f"SUCCESS: Found Invoice {invoice.id}")
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv_id).all()
        print(f"Direct Query Items Count: {len(items)}")
        for i in items:
            print(f" - {i.product_name} (id: {i.id})")
            
        print(f"Relationship Items Count: {len(invoice.items)}")
        for i in invoice.items:
            print(f" - {i.product_name} (id: {i.id})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check()

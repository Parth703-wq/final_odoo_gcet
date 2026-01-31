
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pydantic import ValidationError

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
from app.schemas.invoice import InvoiceResponse, InvoiceItemResponse

def check_serialization():
    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(Invoice.id == 7).first()
        if not invoice:
            print("Invoice 7 not found")
            return
        
        print(f"Attribute 'items' type: {type(invoice.items)}")
        print(f"Attribute 'items' value: {invoice.items}")
        
        # Check __dict__
        print(f"Raw __dict__ keys: {invoice.__dict__.keys()}")
        if 'items' in invoice.__dict__:
            print(f"Items in __dict__: {invoice.__dict__['items']}")
        else:
            print("'items' NOT in __dict__ (lazy loaded or not accessed yet)")
            
        # Trigger load
        count = len(invoice.items)
        print(f"Triggered load, count: {count}")
        print(f"Items now in __dict__: {'items' in invoice.__dict__}")
        
        # Test serialization again
        pydantic_model = InvoiceResponse.model_validate(invoice)
        print(f"Pydantic items count: {len(pydantic_model.items)}")
        if len(pydantic_model.items) == 0:
            print("!!! STILL ZERO !!!")
            # Try manual build
            manual_items = [InvoiceItemResponse.model_validate(i) for i in invoice.items]
            print(f"Manual items serialization count: {len(manual_items)}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_serialization()

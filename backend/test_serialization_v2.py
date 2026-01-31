
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import json
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
        
        print(f"SQLAlchemy Invoice ID: {invoice.id}")
        print(f"SQLAlchemy Items Count: {len(invoice.items)}")
        
        if len(invoice.items) > 0:
            item = invoice.items[0]
            print(f"First Item: {item.product_name}")
            try:
                serialized_item = InvoiceItemResponse.model_validate(item)
                print("✓ First item serialized successfully")
            except ValidationError as e:
                print("✗ First item serialization FAILED:")
                print(e)
            except Exception as e:
                print(f"! Unexpected error serializing item: {e}")
        
        try:
            pydantic_model = InvoiceResponse.model_validate(invoice)
            print("✓ Full invoice serialized successfully")
            print(f"Items in model: {len(pydantic_model.items)}")
        except ValidationError as e:
            print("✗ Full invoice serialization FAILED:")
            print(e)
            
    finally:
        db.close()

if __name__ == "__main__":
    check_serialization()

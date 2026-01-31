
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
        
        print(f"SQLAlchemy Items Count: {len(invoice.items)}")
        
        # Test serialization again
        pydantic_model = InvoiceResponse.model_validate(invoice)
        # Check both aliased if possible or just the field name
        items_count = len(getattr(pydantic_model, 'line_items', []))
        print(f"Pydantic line_items count: {items_count}")
        
        if items_count == 0:
            print("!!! STILL ZERO !!!")
            # Dump the model content
            print("Model dump (aliased=False):", pydantic_model.model_dump())
            print("Model items from dict:", pydantic_model.model_dump().get('items'))
            
    finally:
        db.close()

if __name__ == "__main__":
    check_serialization()

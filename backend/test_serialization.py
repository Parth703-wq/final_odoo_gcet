
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import json
from datetime import datetime

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
from app.schemas.invoice import InvoiceResponse

def check_serialization():
    db = SessionLocal()
    try:
        invoice = db.query(Invoice).filter(Invoice.id == 7).first()
        if not invoice:
            print("Invoice 7 not found")
            return
        
        # Manually verify items exist in session
        print(f"SQLAlchemy Items Count: {len(invoice.items)}")
        
        # Test Pydantic serialization
        try:
            pydantic_model = InvoiceResponse.model_validate(invoice)
            json_str = pydantic_model.model_dump_json(indent=2)
            print("--- Pydantic Serialized JSON ---")
            print(json_str)
            
            # Check if items are in the dict
            data = pydantic_model.model_dump()
            print(f"\nPydantic Items Count: {len(data.get('items', []))}")
            
        except Exception as e:
            print(f"Pydantic Serialization Error: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    check_serialization()

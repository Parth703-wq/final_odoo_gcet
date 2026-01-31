
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
from app.models.order import Order

def check_data():
    db = SessionLocal()
    try:
        # Check specific invoice 7
        invoice = db.query(Invoice).filter(Invoice.id == 7).first()
        if not invoice:
            print("Invoice 7 not found")
            # Check last invoice
            invoice = db.query(Invoice).order_by(Invoice.id.desc()).first()
            if not invoice:
                print("No invoices found at all")
                return
        
        print(f"Checking Invoice ID: {invoice.id}, Number: {invoice.invoice_number}")
        print(f"Status: {invoice.status}")
        print(f"Order ID: {invoice.order_id}")
        
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        print(f"Invoice Items (via direct query) Count: {len(items)}")
        for item in items:
            print(f" - {item.product_name}: {item.quantity} x {item.unit_price} = {item.line_total}")
            
        print(f"Invoice.items relationship count: {len(invoice.items)}")
        
        order = db.query(Order).filter(Order.id == invoice.order_id).first()
        if order:
            print(f"Order ID {order.id} Items Count: {len(order.items)}")
            for item in order.items:
                print(f" - {item.product_name}: {item.quantity}")
        else:
            print("Order not found!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()

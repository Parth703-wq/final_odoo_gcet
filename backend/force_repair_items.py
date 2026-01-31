
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

def force_repair():
    db = SessionLocal()
    try:
        inv_id = 7
        invoice = db.query(Invoice).filter(Invoice.id == inv_id).first()
        if not invoice:
            print("Invoice 7 not found")
            return
            
        order = db.query(Order).filter(Order.id == invoice.order_id).first()
        if not order:
            print(f"Order {invoice.order_id} not found")
            return
            
        print(f"Repairing Invoice {inv_id} from Order {order.id}")
        
        # 1. Clear items
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv_id).delete()
        db.commit()
        
        # 2. Add from order_items
        for oi in order.items:
            print(f"Adding item: {oi.product_name}")
            tax_rate = order.tax_rate or 18.0
            tax_amount = oi.quantity * oi.unit_price * (tax_rate / 100)
            
            ii = InvoiceItem(
                invoice_id=inv_id,
                product_name=oi.product_name,
                product_sku=oi.product_sku,
                description=f"Rental: {oi.rental_start_date} to {oi.rental_end_date}",
                rental_start_date=oi.rental_start_date,
                rental_end_date=oi.rental_end_date,
                quantity=oi.quantity,
                unit="Units",
                unit_price=oi.unit_price,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                cgst=tax_amount / 2,
                sgst=tax_amount / 2,
                igst=0.0,
                line_total=(oi.quantity * oi.unit_price) + tax_amount
            )
            db.add(ii)
            
        # 3. Handle deposit
        if order.security_deposit > 0:
            print("Adding security deposit item")
            di = InvoiceItem(
                invoice_id=inv_id,
                product_name="Security Deposit",
                description="Refundable security deposit",
                quantity=1,
                unit="Units",
                unit_price=order.security_deposit,
                tax_rate=0.0,
                tax_amount=0.0,
                line_total=order.security_deposit
            )
            db.add(di)
            
        db.commit()
        
        # 4. Final check
        count = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == inv_id).count()
        print(f"VERIFIED: Invoice {inv_id} now has {count} items in database.")
        
    finally:
        db.close()

if __name__ == "__main__":
    force_repair()

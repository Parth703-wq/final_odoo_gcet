
import os
import sys

# Add the project root to sys.path to allow imports from 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.order import Order, OrderStatus
from app.services.invoice_service import InvoiceService

def force_generate():
    db = SessionLocal()
    try:
        # Find all confirmed/sale orders
        orders = db.query(Order).filter(Order.status == OrderStatus.SALE_ORDER).all()
        print(f"Found {len(orders)} confirmed orders.")
        
        invoice_service = InvoiceService(db)
        
        for order in orders:
            # Check if invoice already exists
            if order.invoices.count() == 0:
                print(f"Generating invoice for Order {order.order_number}...")
                try:
                    invoice_service.create_invoice_from_order(order.id)
                    print(f"Success!")
                except Exception as e:
                    print(f"Failed for {order.order_number}: {e}")
            else:
                print(f"Order {order.order_number} already has {order.invoices.count()} invoices.")
                
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_generate()

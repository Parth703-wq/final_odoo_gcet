
from app.core.database import SessionLocal
from app.models.invoice import Invoice, InvoiceItem
from app.models.order import Order

def check_data():
    db = SessionLocal()
    try:
        last_invoice = db.query(Invoice).order_by(Invoice.id.desc()).first()
        if not last_invoice:
            print("No invoices found")
            return
        
        print(f"Checking Invoice ID: {last_invoice.id}, Number: {last_invoice.invoice_number}")
        print(f"Order ID: {last_invoice.order_id}")
        
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == last_invoice.id).all()
        print(f"Invoice Items Count: {len(items)}")
        for item in items:
            print(f" - {item.product_name}: {item.quantity} x {item.unit_price}")
            
        order = db.query(Order).filter(Order.id == last_invoice.order_id).first()
        if order:
            print(f"Order Items Count: {len(order.items)}")
            for item in order.items:
                print(f" - {item.product_name}: {item.quantity}")
        else:
            print("Order not found!")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_data()

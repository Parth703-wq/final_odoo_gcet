import requests
import json

def test_invoice_api():
    base_url = "http://localhost:8000/api/v1"
    
    # We need a token. Let's try to get one for the first user
    print("Getting token for customer...")
    # NOTE: This assumes we know the password or can bypass it for testing
    # Since I don't have the password, I'll try to use the debug logic to get a token if possible,
    # or just run a script that calls the function directly and prints the result of InvoiceResponse.model_validate
    
    # Better approach: Test validation directly in a script
    from app.core.database import SessionLocal
    from app.schemas.invoice import InvoiceResponse
    from app.models.invoice import Invoice
    from app.services.invoice_service import InvoiceService
    from app.models.order import Order
    
    db = SessionLocal()
    try:
        order = db.query(Order).order_by(Order.id.desc()).first()
        print(f"Testing with Order ID: {order.id}")
        
        service = InvoiceService(db)
        try:
            invoice = service.create_invoice_from_order(order.id)
            print(f"Invoice {invoice.id} retrieved/created.")
            
            # Now test Pydantic validation
            try:
                pydantic_inv = InvoiceResponse.model_validate(invoice)
                print("Pydantic validation: SUCCESS")
                print(json.dumps(pydantic_inv.model_dump(), default=str, indent=2))
            except Exception as ve:
                print(f"Pydantic validation: FAILURE: {ve}")
                
        except Exception as e:
            print(f"Service logic: FAILURE: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == '__main__':
    test_invoice_api()

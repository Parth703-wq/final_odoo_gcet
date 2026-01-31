from app.core.database import SessionLocal
from app.schemas.invoice import InvoiceResponse
from app.models.invoice import Invoice
from app.services.invoice_service import InvoiceService
from app.models.order import Order

def test_minimal():
    db = SessionLocal()
    try:
        order = db.query(Order).order_by(Order.id.desc()).first()
        service = InvoiceService(db)
        invoice = service.create_invoice_from_order(order.id)
        
        try:
            InvoiceResponse.model_validate(invoice)
            print("VALIDATION_SUCCESS")
        except Exception as e:
            print(f"VALIDATION_FAILURE: {str(e)}")
            # Print specific validation errors if it's a Pydantic error
            from pydantic import ValidationError
            if isinstance(e, ValidationError):
                print("Detailed errors:")
                for error in e.errors():
                    print(f"  Field: {error['loc']}, Msg: {error['msg']}, Type: {error['type']}")
                    
    finally:
        db.close()

if __name__ == '__main__':
    test_minimal()

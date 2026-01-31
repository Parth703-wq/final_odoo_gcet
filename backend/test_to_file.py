from app.core.database import SessionLocal
from app.schemas.invoice import InvoiceResponse
from app.models.invoice import Invoice
from app.services.invoice_service import InvoiceService
from app.models.order import Order
import traceback

def test_to_file():
    db = SessionLocal()
    with open("validation_result.txt", "w") as f:
        try:
            order = db.query(Order).order_by(Order.id.desc()).first()
            f.write(f"Testing with Order ID: {order.id}\n")
            
            service = InvoiceService(db)
            invoice = service.create_invoice_from_order(order.id)
            f.write(f"Invoice ID: {invoice.id}\n")
            
            try:
                InvoiceResponse.model_validate(invoice)
                f.write("VALIDATION_SUCCESS\n")
            except Exception as e:
                f.write(f"VALIDATION_FAILURE: {str(e)}\n\n")
                from pydantic import ValidationError
                if isinstance(e, ValidationError):
                    f.write("Detailed errors:\n")
                    for error in e.errors():
                        f.write(f"  Field: {error['loc']}, Msg: {error['msg']}, Type: {error['type']}\n")
                else:
                    f.write(traceback.format_exc())
                    
        except Exception as e:
            f.write(f"GLOBAL_FAILURE: {str(e)}\n")
            f.write(traceback.format_exc())
        finally:
            db.close()

if __name__ == '__main__':
    test_to_file()

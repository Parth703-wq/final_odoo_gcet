
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

from app.models.invoice import Invoice, InvoiceStatus
from app.services.invoice_service import InvoiceService

def repair():
    db = SessionLocal()
    try:
        service = InvoiceService(db)
        # Force Invoice 7 to DRAFT if it's not (to allow overwrite)
        invoice = db.query(Invoice).filter(Invoice.id == 7).first()
        if invoice:
            print(f"Repairing Invoice {invoice.id} ({invoice.invoice_number})")
            invoice.status = InvoiceStatus.DRAFT
            db.commit()
            
            # Re-run the creation logic which pulls items from the order
            repaired_invoice = service.create_invoice_from_order(invoice.order_id)
            db.commit()
            
            print(f"SUCCESS: Repaired Invoice 7. Item count is now: {len(repaired_invoice.items)}")
            for item in repaired_invoice.items:
                print(f" - {item.product_name}: {item.line_total}")
        else:
            print("Invoice 7 not found!")
            
    except Exception as e:
        print(f"REPAIR FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    repair()

import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.product_service import ProductService

def test_get_products():
    db = SessionLocal()
    try:
        service = ProductService(db)
        print("Fetching products...")
        result = service.get_products()
        print(f"Success! Found {result['total']} products.")
    except Exception as e:
        print("Error fetching products:")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_get_products()

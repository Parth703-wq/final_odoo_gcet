"""Fix products is_published and is_rentable fields in MySQL"""
from app.core.database import SessionLocal
from app.models.product import Product

db = SessionLocal()

# Get all products
products = db.query(Product).all()
print(f"Found {len(products)} products")

# Update all products to be published and rentable
for p in products:
    print(f"Product: {p.name}, is_published: {p.is_published}, is_rentable: {p.is_rentable}")
    p.is_published = True
    p.is_rentable = True

db.commit()
print("\nAll products updated to is_published=True and is_rentable=True")
db.close()

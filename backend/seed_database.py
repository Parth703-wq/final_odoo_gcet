"""
Seed database with test accounts and sample data
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.product import Product, Category
from app.models.settings import CompanySettings

def create_test_accounts(db: Session):
    """Create test accounts for admin, vendor, and customer"""
    
    print("Creating test accounts...")
    
    # 1. ADMIN ACCOUNT
    admin = User(
        email="admin@rental.com",
        password_hash=get_password_hash("Admin@123"),
        first_name="Admin",
        last_name="User",
        phone="+91 98765 43210",
        role=UserRole.ADMIN,
        is_active=True,
        address_line1="Admin Office, Mumbai",
        city="Mumbai",
        state="Maharashtra",
        zip_code="400001"
    )
    db.add(admin)
    print("[OK] Admin account created: admin@rental.com / Admin@123")
    
    # 2. VENDOR ACCOUNT
    vendor = User(
        email="vendor@rental.com",
        password_hash=get_password_hash("Vendor@123"),
        first_name="Raj",
        last_name="Sharma",
        phone="+91 98765 43211",
        role=UserRole.VENDOR,
        is_active=True,
        company_name="Tech Rentals Pvt Ltd",
        gstin="27AABCT1234C1Z5",
        address_line1="Shop 12, Andheri East",
        city="Mumbai",
        state="Maharashtra",
        zip_code="400069"
    )
    db.add(vendor)
    db.flush()  # Get vendor ID
    print("[OK] Vendor account created: vendor@rental.com / Vendor@123")
    
    # 3. CUSTOMER ACCOUNT
    customer = User(
        email="customer@rental.com",
        password_hash=get_password_hash("Customer@123"),
        first_name="Priya",
        last_name="Patel",
        phone="+91 98765 43212",
        role=UserRole.CUSTOMER,
        is_active=True,
        address_line1="Bandra West, Mumbai",
        city="Mumbai",
        state="Maharashtra",
        zip_code="400050"
    )
    db.add(customer)
    print("[OK] Customer account created: customer@rental.com / Customer@123")
    
    db.commit()
    return vendor.id

def create_categories(db: Session):
    """Create product categories"""
    
    print("\nCreating categories...")
    
    categories = [
        Category(name="Electronics", description="Electronic equipment and gadgets"),
        Category(name="Furniture", description="Office and home furniture"),
        Category(name="Photography", description="Cameras and photography equipment"),
        Category(name="Events", description="Event equipment and supplies"),
        Category(name="Tools", description="Power tools and equipment"),
    ]
    
    for cat in categories:
        db.add(cat)
    
    db.commit()
    print(f"[OK] Created {len(categories)} categories")
    return {cat.name: cat.id for cat in categories}

def create_sample_products(db: Session, vendor_id: int, categories: dict):
    """Create sample products for the vendor"""
    
    print("\nCreating sample products...")
    
    products = [
        Product(
            vendor_id=vendor_id,
            name="Canon EOS R6 Camera",
            description="Professional mirrorless camera with 20MP full-frame sensor. Perfect for photography and videography.",
            sku="CAM-R6-001",
            category_id=categories.get("Photography"),
            cost_price=150000,
            sales_price=180000,
            rental_price_daily=2500,
            rental_price_weekly=15000,
            rental_price_monthly=50000,
            security_deposit=20000,
            quantity_on_hand=3,
            brand="Canon",
            color="Black",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=Canon+EOS+R6"
        ),
        Product(
            vendor_id=vendor_id,
            name="MacBook Pro 16\" M3",
            description="Latest MacBook Pro with M3 Max chip, 36GB RAM, 1TB SSD. Ideal for video editing and development.",
            sku="LAP-MBP-001",
            category_id=categories.get("Electronics"),
            cost_price=250000,
            sales_price=300000,
            rental_price_daily=3000,
            rental_price_weekly=18000,
            rental_price_monthly=60000,
            security_deposit=30000,
            quantity_on_hand=5,
            brand="Apple",
            color="Space Gray",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=MacBook+Pro"
        ),
        Product(
            vendor_id=vendor_id,
            name="DJI Mavic 3 Pro Drone",
            description="Professional drone with 4/3 CMOS Hasselblad camera. Ideal for aerial photography and videography.",
            sku="DRN-MV3-001",
            category_id=categories.get("Photography"),
            cost_price=180000,
            sales_price=220000,
            rental_price_daily=4000,
            rental_price_weekly=25000,
            rental_price_monthly=80000,
            security_deposit=40000,
            quantity_on_hand=2,
            brand="DJI",
            color="Gray",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=DJI+Mavic+3"
        ),
        Product(
            vendor_id=vendor_id,
            name="Professional Projector 4K",
            description="4K Ultra HD projector with 3000 lumens brightness. Perfect for presentations and events.",
            sku="PRJ-4K-001",
            category_id=categories.get("Events"),
            cost_price=80000,
            sales_price=100000,
            rental_price_daily=2000,
            rental_price_weekly=12000,
            rental_price_monthly=40000,
            security_deposit=15000,
            quantity_on_hand=4,
            brand="Epson",
            color="White",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=Projector+4K"
        ),
        Product(
            vendor_id=vendor_id,
            name="Gaming PC - RTX 4090",
            description="High-end gaming PC with RTX 4090, i9-13900K, 64GB RAM, 2TB NVMe SSD.",
            sku="PC-GAM-001",
            category_id=categories.get("Electronics"),
            cost_price=400000,
            sales_price=500000,
            rental_price_daily=5000,
            rental_price_weekly=30000,
            rental_price_monthly=100000,
            security_deposit=50000,
            quantity_on_hand=2,
            brand="Custom Build",
            color="RGB",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=Gaming+PC"
        ),
        Product(
            vendor_id=vendor_id,
            name="Herman Miller Aeron Chair",
            description="Ergonomic office chair with lumbar support. Perfect for long working hours.",
            sku="FUR-CHR-001",
            category_id=categories.get("Furniture"),
            cost_price=80000,
            sales_price=100000,
            rental_price_daily=500,
            rental_price_weekly=3000,
            rental_price_monthly=10000,
            security_deposit=5000,
            quantity_on_hand=10,
            brand="Herman Miller",
            color="Black",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=Aeron+Chair"
        ),
        Product(
            vendor_id=vendor_id,
            name="Sony A7 IV Camera",
            description="33MP full-frame mirrorless camera with 4K 60fps video recording.",
            sku="CAM-A74-001",
            category_id=categories.get("Photography"),
            cost_price=200000,
            sales_price=250000,
            rental_price_daily=3000,
            rental_price_weekly=18000,
            rental_price_monthly=60000,
            security_deposit=25000,
            quantity_on_hand=2,
            brand="Sony",
            color="Black",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=Sony+A7+IV"
        ),
        Product(
            vendor_id=vendor_id,
            name="Makita Impact Driver Kit",
            description="Professional cordless impact driver with 2 batteries and charger.",
            sku="TOL-IMP-001",
            category_id=categories.get("Tools"),
            cost_price=15000,
            sales_price=20000,
            rental_price_daily=300,
            rental_price_weekly=1800,
            rental_price_monthly=6000,
            security_deposit=3000,
            quantity_on_hand=8,
            brand="Makita",
            color="Blue",
            is_published=True,
            is_rentable=True,
            image_url="https://via.placeholder.com/400x400.png?text=Impact+Driver"
        ),
    ]
    
    for product in products:
        db.add(product)
    
    db.commit()
    print(f"[OK] Created {len(products)} sample products")

def create_company_settings(db: Session):
    """Create default company settings"""
    
    print("\nCreating company settings...")
    
    settings = CompanySettings(
        company_name="Rental Management System",
        gst_rate=18.0,
        late_fee_per_day=100.0,
        late_fee_percentage=5.0
    )
    
    db.add(settings)
    db.commit()
    print("[OK] Company settings created")

def main():
    print("="*60)
    print("  DATABASE SEEDING - TEST ACCOUNTS & SAMPLE DATA")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("\n[WARN] Database already has users!")
            response = input("Do you want to delete existing data and recreate? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
            
            # Clear existing data
            db.query(Product).delete()
            db.query(Category).delete()
            db.query(User).delete()
            db.query(CompanySettings).delete()
            db.commit()
            print("[OK] Cleared existing data")
        
        # Create test data
        vendor_id = create_test_accounts(db)
        categories = create_categories(db)
        create_sample_products(db, vendor_id, categories)
        create_company_settings(db)
        
        print("\n" + "="*60)
        print("  [SUCCESS] DATABASE SEEDED SUCCESSFULLY!")
        print("="*60)
        print("\n TEST ACCOUNT CREDENTIALS:\n")
        print("ADMIN:")
        print("  Email: admin@rental.com")
        print("  Password: Admin@123")
        print("  Role: Full system access\n")
        
        print("VENDOR:")
        print("  Email: vendor@rental.com")
        print("  Password: Vendor@123")
        print("  Role: Manage products & orders\n")
        
        print("CUSTOMER:")
        print("  Email: customer@rental.com")
        print("  Password: Customer@123")
        print("  Role: Browse & rent products\n")
        
        print("="*60)
        print(" You can now login at: http://localhost:3000/login")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()


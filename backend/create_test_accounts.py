"""
Simple script to create test accounts
"""
import sys
from datetime import datetime  
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole

def main():
    print("="*60)
    print("  CREATING TEST ACCOUNTS")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Check existing users
        existing = db.query(User).filter(User.email.in_([
            "admin@rental.com", "vendor@rental.com", "customer@rental.com"
        ])).all()
        
        if existing:
            print("\n[INFO] Some test accounts already exist. Deleting...")
            for user in existing:
                db.delete(user)
            db.commit()
       
        print("\nCreating test accounts...")
        
        # 1. ADMIN
        admin = User(
            email="admin@rental.com",
            password_hash=get_password_hash("Admin@123"),
            first_name="Admin",
            last_name="User",
            phone="+91 9876543210",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        
        # 2. VENDOR
        vendor = User(
            email="vendor@rental.com",
            password_hash=get_password_hash("Vendor@123"),
            first_name="Raj",
            last_name="Sharma",
            phone="+91 9876543211",
            role=UserRole.VENDOR,
            is_active=True,
            company_name="Tech Rentals Pvt Ltd",
            gstin="27AABCT1234C1Z5"
        )
        db.add(vendor)
        
        # 3. CUSTOMER
        customer = User(
            email="customer@rental.com",
            password_hash=get_password_hash("Customer@123"),
            first_name="Priya",
            last_name="Patel",
            phone="+91 9876543212",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db.add(customer)
        
        db.commit()
        
        print("\n" + "="*60)
        print("  SUCCESS! TEST ACCOUNTS CREATED")
        print("="*60)
        print("\nLogin Credentials:\n")
        print("ADMIN:")
        print("  Email: admin@rental.com")
        print("  Password: Admin@123\n")
        
        print("VENDOR:")
        print("  Email: vendor@rental.com")
        print("  Password: Vendor@123\n")
        
        print("CUSTOMER:")
        print("  Email: customer@rental.com")
        print("  Password: Customer@123\n")
        
        print("="*60)
        print("Login at: http://localhost:3000/login")
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

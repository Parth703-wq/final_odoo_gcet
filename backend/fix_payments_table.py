"""Add missing columns to payments table"""
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE payments ADD COLUMN customer_id INT NULL"))
        print("Added customer_id column")
    except Exception as e:
        print(f"customer_id: {e}")
    
    try:
        conn.execute(text("ALTER TABLE payments ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'"))
        print("Added currency column")
    except Exception as e:
        print(f"currency: {e}")
    
    try:
        conn.execute(text("ALTER TABLE payments ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
        print("Added updated_at column")
    except Exception as e:
        print(f"updated_at: {e}")
    
    conn.commit()
    print("Done!")

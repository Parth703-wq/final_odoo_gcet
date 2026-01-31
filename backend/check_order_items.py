
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
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

def check_order():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT order_id FROM invoices WHERE id = 7"))
        order_id = res.fetchone()[0]
        print(f"Invoice 7 is linked to Order ID: {order_id}")
        
        res = conn.execute(text(f"SELECT id, product_name, quantity FROM order_items WHERE order_id = {order_id}"))
        items = res.fetchall()
        print(f"Order {order_id} has {len(items)} items:")
        for i in items:
            print(f" - {i[1]} (id: {i[0]}, qty: {i[2]})")

if __name__ == "__main__":
    check_order()

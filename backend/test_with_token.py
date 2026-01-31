import requests
import json
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

def test_with_token():
    db = SessionLocal()
    try:
        # Get a customer user
        user = db.query(User).filter(User.role == "customer").first()
        if not user:
            print("No customer found")
            return
            
        print(f"Testing as user: {user.email}")
        
        # Manually create a token for this user
        token = create_access_token(data={"sub": user.email})
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {"order_id": 1}
        
        print("Sending request to /api/v1/invoices ...")
        response = requests.post("http://localhost:8000/api/v1/invoices", headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Raw Response: {response.text}")
            
    finally:
        db.close()

if __name__ == '__main__':
    test_with_token()

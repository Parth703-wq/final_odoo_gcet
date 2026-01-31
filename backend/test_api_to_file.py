import requests
import json
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

def test_to_file():
    db = SessionLocal()
    with open("api_test_result.txt", "w") as f:
        try:
            # Get a customer user
            user = db.query(User).filter(User.role == "customer").first()
            if not user:
                f.write("No customer found\n")
                return
                
            f.write(f"Testing as user: {user.email}\n")
            
            # Manually create a token for this user
            token = create_access_token(data={"sub": str(user.id)})
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {"order_id": 1}
            
            f.write("Sending request to /api/v1/invoices ...\n")
            response = requests.post("http://localhost:8000/api/v1/invoices", headers=headers, json=data)
            
            f.write(f"Status Code: {response.status_code}\n")
            try:
                f.write(f"Response: {json.dumps(response.json(), indent=2)}\n")
            except:
                f.write(f"Raw Response: {response.text}\n")
                
        except Exception as e:
            f.write(f"ERROR: {str(e)}\n")
        finally:
            db.close()

if __name__ == '__main__':
    test_to_file()

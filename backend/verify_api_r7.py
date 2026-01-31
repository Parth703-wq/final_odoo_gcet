
import requests
import json

try:
    url = 'http://localhost:8001/api/v1/invoices/7'
    print(f"Calling: {url}")
    r = requests.get(url)
    print(f"Status Code: {r.status_code}")
    data = r.json()
    items = data.get('items', [])
    print(f"Items Count in Payload: {len(items)}")
    for i in items:
        print(f" - {i.get('product_name')}")
except Exception as e:
    print(f"Error: {e}")


import requests
import json

def test_invoice():
    url = "http://localhost:8000/invoices/7"
    # Assuming no auth required for now to check if items are there, 
    # but wait, I know it needs a token.
    # I'll just check if uvicorn logs show items when I hit it from the browser.
    # I'll add logging to the endpoint itself!
    pass

if __name__ == "__main__":
    test_invoice()

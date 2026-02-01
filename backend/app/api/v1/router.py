"""
API v1 Router
"""

from fastapi import APIRouter

<<<<<<< HEAD
from app.api.v1.endpoints import auth, products, orders, invoices, dashboard, admin, payments
=======
from app.api.v1.endpoints import auth, products, orders, invoices, dashboard, admin, reviews, complaints, payments
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(invoices.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)
<<<<<<< HEAD
=======
api_router.include_router(reviews.router)
api_router.include_router(complaints.router)
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
api_router.include_router(payments.router)

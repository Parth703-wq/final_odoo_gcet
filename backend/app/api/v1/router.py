"""
API v1 Router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, products, orders, invoices, dashboard, admin

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(invoices.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)

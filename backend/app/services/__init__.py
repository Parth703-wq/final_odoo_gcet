"""
Services Package
Exports all services
"""

from app.services.auth_service import AuthService
from app.services.email_service import (
    send_password_reset_email,
    send_order_confirmation_email,
    send_invoice_email,
    send_return_reminder_email,
    send_late_return_alert
)
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.services.invoice_service import InvoiceService
from app.services.dashboard_service import DashboardService

__all__ = [
    "AuthService",
    "ProductService",
    "OrderService",
    "InvoiceService",
    "DashboardService",
    "send_password_reset_email",
    "send_order_confirmation_email",
    "send_invoice_email",
    "send_return_reminder_email",
    "send_late_return_alert"
]

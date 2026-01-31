"""
Models Package
Exports all models for easy importing
"""

from app.models.user import User, UserRole
from app.models.product import Product, ProductVariant, Category, ProductAttribute, RentalPeriodType
from app.models.order import Order, OrderItem, OrderStatus, DeliveryMethod
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.reservation import Reservation, PickupDocument, ReturnDocument, ReservationStatus, StockStatus
from app.models.settings import RentalPeriodConfig, CompanySettings, Coupon, Notification

__all__ = [
    # User
    "User", "UserRole",
    
    # Product
    "Product", "ProductVariant", "Category", "ProductAttribute", "RentalPeriodType",
    
    # Order
    "Order", "OrderItem", "OrderStatus", "DeliveryMethod",
    
    # Invoice
    "Invoice", "InvoiceItem", "Payment", "InvoiceStatus", "PaymentStatus", "PaymentMethod",
    
    # Reservation
    "Reservation", "PickupDocument", "ReturnDocument", "ReservationStatus", "StockStatus",
    
    # Settings
    "RentalPeriodConfig", "CompanySettings", "Coupon", "Notification",
]

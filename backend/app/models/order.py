"""
Order Model
Handles Quotations and Sale Orders (Rental Orders)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    QUOTATION = "quotation"
    QUOTATION_SENT = "quotation_sent"
    SALE_ORDER = "sale_order"
    CONFIRMED = "confirmed"
    PICKED_UP = "picked_up"
    ACTIVE = "active"
    RETURNED = "returned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    LATE = "late"


class DeliveryMethod(str, enum.Enum):
    """Delivery method"""
    STANDARD = "standard"
    PICKUP = "pickup"


class Order(Base):
    """Order model - represents Quotation → Sale Order"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer & Vendor
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.QUOTATION, nullable=False)
    
    # Rental Period
    rental_start_date = Column(DateTime, nullable=False)
    rental_end_date = Column(DateTime, nullable=False)
    
    # Addresses
    billing_address = Column(Text, nullable=True)
    delivery_address = Column(Text, nullable=True)
    
    # Delivery
    delivery_method = Column(Enum(DeliveryMethod), default=DeliveryMethod.STANDARD)
    delivery_charges = Column(Float, default=0.0)
    
    # Pricing
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=18.0)  # GST 18%
    discount_amount = Column(Float, default=0.0)
    discount_code = Column(String(50), nullable=True)
    security_deposit = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Downpayment
    downpayment_amount = Column(Float, default=0.0)
    downpayment_paid = Column(Boolean, default=False)
    
    # Late Fees
    late_fee_per_day = Column(Float, default=0.0)
    late_fees_applied = Column(Float, default=0.0)
    actual_return_date = Column(DateTime, nullable=True)
    
    # Pickup & Return
    pickup_date = Column(DateTime, nullable=True)
    pickup_notes = Column(Text, nullable=True)
    return_date = Column(DateTime, nullable=True)
    return_notes = Column(Text, nullable=True)
    
    # Notes
    customer_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Timestamps
    order_date = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="orders", foreign_keys=[customer_id])
    vendor = relationship("User", back_populates="vendor_orders", foreign_keys=[vendor_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="order", lazy="dynamic")
    reservations = relationship("Reservation", back_populates="order", lazy="dynamic")
<<<<<<< HEAD
    payments = relationship("Payment", back_populates="order")
=======
    payments = relationship("Payment", back_populates="order", lazy="dynamic")
    
    @property
    def invoice(self):
        """Returns the primary (first) invoice for this order"""
        return self.invoices.first()
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
    
    def calculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = sum(item.line_subtotal for item in self.items)
        self.tax_amount = sum(item.tax_amount for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount + self.delivery_charges + self.security_deposit - self.discount_amount
    
    @property
    def is_overdue(self) -> bool:
        """Check if rental is overdue"""
        if self.status in [OrderStatus.PICKED_UP, OrderStatus.ACTIVE]:
            return datetime.utcnow() > self.rental_end_date
        return False


class OrderItem(Base):
    """Order line items"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    
    # Product snapshot (in case product details change)
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=True)
    
    # Rental Period for this item
    rental_start_date = Column(DateTime, nullable=False)
    rental_end_date = Column(DateTime, nullable=False)
    
    # Quantity & Pricing
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    rental_period_type = Column(String(20), default="daily")  # hourly, daily, weekly, monthly
    
    # Calculated
    line_subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    line_total = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    def calculate_total(self, tax_rate: float = 18.0):
        """Calculate line total based on duration and quantity"""
        duration = 1
        if self.rental_start_date and self.rental_end_date:
            delta = self.rental_end_date - self.rental_start_date
            if self.rental_period_type == "hourly":
                duration = max(1, int(delta.total_seconds() / 3600))
            elif self.rental_period_type == "daily":
                duration = max(1, delta.days)
            elif self.rental_period_type == "weekly":
                duration = max(1, delta.days // 7)
            elif self.rental_period_type == "monthly":
                duration = max(1, delta.days // 30)
        
        self.line_subtotal = self.quantity * self.unit_price * duration
        self.tax_amount = self.line_subtotal * (tax_rate / 100)
        self.line_total = self.line_subtotal + self.tax_amount

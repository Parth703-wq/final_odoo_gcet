"""
Invoice Model
Handles invoicing and payments
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status"""
    DRAFT = "draft"
    SENT = "sent"
    POSTED = "posted"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """Payment method"""
    RAZORPAY = "razorpay"
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    CASH = "cash"


class Invoice(Base):
    """Invoice model"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # References
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    
    # Dates
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    
    # Rental Period
    rental_start_date = Column(DateTime, nullable=False)
    rental_end_date = Column(DateTime, nullable=False)
    
    # Addresses
    billing_address = Column(Text, nullable=True)
    delivery_address = Column(Text, nullable=True)
    
    # Company Info (Vendor)
    vendor_company_name = Column(String(255), nullable=True)
    vendor_gstin = Column(String(15), nullable=True)
    vendor_logo = Column(String(500), nullable=True)
    
    # Customer Info
    customer_name = Column(String(255), nullable=True)
    customer_gstin = Column(String(15), nullable=True)
    
    # Pricing
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=18.0)
    cgst = Column(Float, default=0.0)  # Central GST
    sgst = Column(Float, default=0.0)  # State GST
    igst = Column(Float, default=0.0)  # Integrated GST
    tax_amount = Column(Float, default=0.0)
    
    discount_amount = Column(Float, default=0.0)
    discount_code = Column(String(50), nullable=True)
    
    security_deposit = Column(Float, default=0.0)
    delivery_charges = Column(Float, default=0.0)
    late_fees = Column(Float, default=0.0)
    
    total_amount = Column(Float, default=0.0)
    
    # Payment
    amount_paid = Column(Float, default=0.0)
    amount_due = Column(Float, default=0.0)
    
    # Notes
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="invoices")
    customer = relationship("User", back_populates="invoices", foreign_keys=[customer_id])
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", lazy="dynamic")
    
    def calculate_gst(self, is_inter_state: bool = False):
        """Calculate GST (CGST + SGST or IGST)"""
        if is_inter_state:
            self.igst = self.subtotal * (self.tax_rate / 100)
            self.cgst = 0.0
            self.sgst = 0.0
        else:
            half_rate = self.tax_rate / 2
            self.cgst = self.subtotal * (half_rate / 100)
            self.sgst = self.subtotal * (half_rate / 100)
            self.igst = 0.0
        
        self.tax_amount = self.cgst + self.sgst + self.igst
    
    def calculate_totals(self):
        """Recalculate invoice totals"""
        self.subtotal = sum(item.line_total for item in self.items)
        self.calculate_gst()
        self.total_amount = (
            self.subtotal + self.tax_amount + self.delivery_charges + 
            self.security_deposit + self.late_fees - self.discount_amount
        )
        self.amount_due = self.total_amount - self.amount_paid


class InvoiceItem(Base):
    """Invoice line items"""
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Product Info
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Rental Period
    rental_start_date = Column(DateTime, nullable=True)
    rental_end_date = Column(DateTime, nullable=True)
    
    # Quantity & Pricing
    quantity = Column(Integer, default=1)
    unit = Column(String(50), default="Units")
    unit_price = Column(Float, nullable=False)
    
    # Tax
    tax_rate = Column(Float, default=18.0)
    tax_amount = Column(Float, default=0.0)
    
    # Total
    line_total = Column(Float, default=0.0)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")


class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_number = Column(String(50), unique=True, index=True)
    
    # References
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # Payment Details
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.RAZORPAY)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Razorpay
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    
    # Card details (masked)
    card_last_four = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)
    
    # Transaction
    transaction_id = Column(String(100), nullable=True)
    transaction_response = Column(JSON, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    payment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")

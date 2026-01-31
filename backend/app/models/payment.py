
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

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
    BANK_TRANSFER = "bank_transfer"

class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payment_number = Column(String(50), unique=True, index=True)
    
    # References
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Payment Details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.RAZORPAY)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Razorpay specific fields
    razorpay_order_id = Column(String(100), unique=True, index=True, nullable=True)
    razorpay_payment_id = Column(String(100), unique=True, index=True, nullable=True)
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
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    order = relationship("Order", back_populates="payments")
    customer = relationship("User", back_populates="payments")

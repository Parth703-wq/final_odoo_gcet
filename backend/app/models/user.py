"""
User Model
Handles Customers, Vendors, and Admins
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    ADMIN = "admin"


class User(Base):
    """User model for all user types"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Basic Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Company Info (for Vendors)
    company_name = Column(String(255), nullable=True)
    company_logo = Column(String(500), nullable=True)
    gstin = Column(String(15), nullable=True)  # GST Identification Number
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    zip_code = Column(String(20), nullable=True)
    
    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Coupon & Referral
    coupon_code_used = Column(String(50), nullable=True)
    
    # Password Reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="vendor", lazy="dynamic")
    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id", lazy="dynamic")
    vendor_orders = relationship("Order", back_populates="vendor", foreign_keys="Order.vendor_id", lazy="dynamic")
    invoices = relationship("Invoice", back_populates="customer", foreign_keys="Invoice.customer_id", lazy="dynamic")
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self) -> str:
        """Get full address string"""
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.zip_code, self.country]
        return ", ".join([p for p in parts if p])

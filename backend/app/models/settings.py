"""
Settings & Configuration Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from datetime import datetime

from app.core.database import Base


class RentalPeriodConfig(Base):
    """Configurable rental periods"""
    __tablename__ = "rental_period_configs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Hourly", "Daily"
    duration_type = Column(String(50), nullable=False)  # hour, day, week, month
    duration_value = Column(Integer, default=1)  # 1, 7, 30, etc.
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class CompanySettings(Base):
    """Company/System settings"""
    __tablename__ = "company_settings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Company Info
    company_name = Column(String(255), nullable=False)
    company_logo = Column(String(500), nullable=True)
    company_address = Column(String(500), nullable=True)
    company_phone = Column(String(20), nullable=True)
    company_email = Column(String(255), nullable=True)
    company_website = Column(String(255), nullable=True)
    
    # GST
    gstin = Column(String(15), nullable=True)
    gst_rate = Column(Float, default=18.0)
    
    # Currency
    currency_code = Column(String(3), default="INR")
    currency_symbol = Column(String(5), default="₹")
    
    # Late Fee
    late_fee_per_day = Column(Float, default=100.0)
    late_fee_percentage = Column(Float, default=5.0)  # % of rental amount
    
    # Terms
    default_terms_conditions = Column(String(2000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Coupon(Base):
    """Discount coupons"""
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Discount
    discount_type = Column(String(20), default="percentage")  # percentage, fixed
    discount_value = Column(Float, nullable=False)
    max_discount = Column(Float, nullable=True)  # Max discount amount
    min_order_value = Column(Float, default=0.0)
    
    # Usage
    usage_limit = Column(Integer, nullable=True)  # Total usage limit
    usage_count = Column(Integer, default=0)
    per_user_limit = Column(Integer, default=1)
    
    # Validity
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    
    title = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)
    notification_type = Column(String(50), default="info")  # info, warning, success, error
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # order, invoice, payment
    reference_id = Column(Integer, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

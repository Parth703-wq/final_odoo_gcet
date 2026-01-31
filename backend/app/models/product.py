"""
Product Model
Handles rentable products with pricing and attributes
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class RentalPeriodType(str, enum.Enum):
    """Rental period types"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Product(Base):
    """Product model for rentable items"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic Info
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(100), unique=True, index=True)
    
    # Images
    image_url = Column(String(500), nullable=True)
    gallery_images = Column(JSON, default=list)  # List of image URLs
    
    # Pricing
    cost_price = Column(Float, default=0.0)
    sales_price = Column(Float, default=0.0)
    
    # Rental Pricing
    rental_price_hourly = Column(Float, default=0.0)
    rental_price_daily = Column(Float, default=0.0)
    rental_price_weekly = Column(Float, default=0.0)
    rental_price_monthly = Column(Float, default=0.0)
    
    # Security Deposit
    security_deposit = Column(Float, default=0.0)
    
    # Inventory
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    
    # Category & Attributes
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    brand = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    attributes = Column(JSON, default=dict)  # Dynamic attributes
    
    # Vendor
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_rentable = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product", lazy="dynamic")
    reservations = relationship("Reservation", back_populates="product", lazy="dynamic")
    variants = relationship("ProductVariant", back_populates="product", lazy="dynamic")
    
    @property
    def available_quantity(self) -> int:
        """Get available quantity (not reserved)"""
        return max(0, self.quantity_on_hand - self.quantity_reserved)
    
    def get_rental_price(self, period_type: RentalPeriodType) -> float:
        """Get rental price for period type"""
        prices = {
            RentalPeriodType.HOURLY: self.rental_price_hourly,
            RentalPeriodType.DAILY: self.rental_price_daily,
            RentalPeriodType.WEEKLY: self.rental_price_weekly,
            RentalPeriodType.MONTHLY: self.rental_price_monthly,
        }
        return prices.get(period_type, self.rental_price_daily)


class ProductVariant(Base):
    """Product variant with different pricing"""
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    name = Column(String(255), nullable=False)  # e.g., "Red - Large"
    sku = Column(String(100), unique=True)
    attributes = Column(JSON, default=dict)  # {"color": "red", "size": "large"}
    
    # Pricing overrides
    rental_price_hourly = Column(Float, nullable=True)
    rental_price_daily = Column(Float, nullable=True)
    rental_price_weekly = Column(Float, nullable=True)
    rental_price_monthly = Column(Float, nullable=True)
    
    # Inventory
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    
    # Relationships
    product = relationship("Product", back_populates="variants")


class Category(Base):
    """Product category"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="category", lazy="dynamic")
    children = relationship("Category", backref="parent", remote_side=[id])


class ProductAttribute(Base):
    """Configurable product attributes (from Settings)"""
    __tablename__ = "product_attributes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Color", "Brand"
    values = Column(JSON, default=list)  # ["Red", "Blue", "Green"]
    
    created_at = Column(DateTime, default=datetime.utcnow)

"""
Reservation Model
Handles stock reservation to prevent double-booking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ReservationStatus(str, enum.Enum):
    """Reservation status"""
    ACTIVE = "active"
    RELEASED = "released"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"


class StockStatus(str, enum.Enum):
    """Stock status for inventory tracking"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    WITH_CUSTOMER = "with_customer"
    RETURNED = "returned"
    MAINTENANCE = "maintenance"


class Reservation(Base):
    """
    Reservation model - blocks stock for a specific period
    Prevents double-booking of products
    """
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # References
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Quantity
    quantity = Column(Integer, nullable=False)
    
    # Reservation Period
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    
    # Status
    status = Column(Enum(ReservationStatus), default=ReservationStatus.ACTIVE)
    stock_status = Column(Enum(StockStatus), default=StockStatus.RESERVED)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="reservations")
    order = relationship("Order", back_populates="reservations")


class PickupDocument(Base):
    """Pickup document generated when order is confirmed"""
    __tablename__ = "pickup_documents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_number = Column(String(50), unique=True, index=True)
    
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Status
    is_picked_up = Column(Boolean, default=False)
    picked_up_at = Column(DateTime, nullable=True)
    picked_up_by = Column(String(255), nullable=True)
    
    # Instructions
    pickup_instructions = Column(String(500), nullable=True)
    pickup_location = Column(String(500), nullable=True)
    
    # Notes
    notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class ReturnDocument(Base):
    """Return document for tracking returns"""
    __tablename__ = "return_documents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_number = Column(String(50), unique=True, index=True)
    
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Status
    is_returned = Column(Boolean, default=False)
    returned_at = Column(DateTime, nullable=True)
    received_by = Column(String(255), nullable=True)
    
    # Condition
    condition_notes = Column(String(500), nullable=True)
    damage_reported = Column(Boolean, default=False)
    damage_description = Column(String(500), nullable=True)
    
    # Late Return
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime, nullable=True)
    is_late = Column(Boolean, default=False)
    late_days = Column(Integer, default=0)
    late_fee_applied = Column(Float, default=0.0)
    
    # Notes
    notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

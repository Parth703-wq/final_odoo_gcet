from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class ComplaintStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class Complaint(Base):
    """Product/Order item complaint model"""
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING)
    
    admin_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", backref="complaints")
    product = relationship("Product", backref="complaints")
    customer = relationship("User", backref="complaints")

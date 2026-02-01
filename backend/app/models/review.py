from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Review(Base):
    """Product review model"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", backref="reviews")
    customer = relationship("User", backref="reviews")
    order = relationship("Order", backref="reviews")

"""
Invoice Model
3: Handles invoicing and payments
4: """

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
    
    def calculate_gst(self):
        """Calculate GST based on subtotal"""
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        # Default to split GST (CGST/SGST)
        self.cgst = self.tax_amount / 2
        self.sgst = self.tax_amount / 2
        self.igst = 0.0 # Standard local rental for now
        
        self.tax_amount = (self.cgst or 0.0) + (self.sgst or 0.0) + (self.igst or 0.0)
    
    def calculate_totals(self):
        """Recalculate invoice totals"""
        # Subtotal should be sum of untaxed amounts from product items only
        product_items = [item for item in self.items if item.product_name != "Security Deposit"]
        self.subtotal = sum(item.quantity * item.unit_price for item in product_items)
        
        # Sum up taxes from items
        self.tax_amount = sum((item.tax_amount or 0.0) for item in self.items)
        self.cgst = sum((item.cgst or 0.0) for item in self.items)
        self.sgst = sum((item.sgst or 0.0) for item in self.items)
        self.igst = sum((item.igst or 0.0) for item in self.items)
        
        # Total amount = subtotal + tax + delivery + deposit + late fees - discount
        subtotal = self.subtotal or 0.0
        tax = self.tax_amount or 0.0
        delivery = self.delivery_charges or 0.0
        deposit = self.security_deposit or 0.0
        late = self.late_fees or 0.0
        discount = self.discount_amount or 0.0
        paid = self.amount_paid or 0.0
        
        self.total_amount = subtotal + tax + delivery + deposit + late - discount
        self.amount_due = self.total_amount - paid


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
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    igst = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    
    # Total
    line_total = Column(Float, default=0.0)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")

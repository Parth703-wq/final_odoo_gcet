"""
Invoice Schemas
Pydantic models for invoice and payment API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.schemas.user import UserResponse

class InvoiceStatusEnum(str, Enum):
    """Invoice status enum"""
    DRAFT = "draft"
    SENT = "sent"
    POSTED = "posted"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethodEnum(str, Enum):
    """Payment method enum"""
    RAZORPAY = "razorpay"
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    CASH = "cash"


class InvoiceItemCreate(BaseModel):
    """Create invoice item"""
    product_name: str
    product_sku: Optional[str] = None
    description: Optional[str] = None
    rental_start_date: Optional[datetime] = None
    rental_end_date: Optional[datetime] = None
    quantity: int = 1
    unit: str = "Units"
    unit_price: float


class InvoiceItemResponse(BaseModel):
    """Invoice item response"""
    id: int
    product_name: str
    product_sku: Optional[str] = None
    description: Optional[str] = None
    rental_start_date: Optional[datetime] = None
    rental_end_date: Optional[datetime] = None
    quantity: int
    unit: str
    unit_price: float
    tax_rate: float
    cgst: float = 0.0
    sgst: float = 0.0
    igst: float = 0.0
    tax_amount: float
    line_total: float
    
    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    """Create invoice from order"""
    order_id: int
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: int
    invoice_number: str
    order_id: int
    customer_id: int
    vendor_id: int
    status: str
    invoice_date: datetime
    due_date: Optional[datetime] = None
    rental_start_date: datetime
    rental_end_date: datetime
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    vendor_company_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    customer_name: Optional[str] = None
    customer_gstin: Optional[str] = None
    subtotal: float
    tax_rate: float
    cgst: float
    sgst: float
    igst: float
    tax_amount: float
    discount_amount: float
    security_deposit: float
    delivery_charges: float
    late_fees: float
    total_amount: float
    amount_paid: float
    amount_due: float
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None
    created_at: datetime
    items: List[InvoiceItemResponse]
    
<<<<<<< HEAD
    model_config = {"from_attributes": True}
=======
    # Add customer details (using forward reference to avoid circular import)
    customer: Optional["UserResponse"] = None
    
    class Config:
        from_attributes = True
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)


class InvoiceListResponse(BaseModel):
    """Paginated invoice list"""
    items: List[InvoiceResponse]
    total: int
    page: int
    per_page: int
    pages: int


# Payment Schemas

class CreateRazorpayOrder(BaseModel):
    """Create Razorpay order for payment"""
    invoice_id: int
    amount: Optional[float] = None  # If partial payment


class RazorpayOrderResponse(BaseModel):
    """Razorpay order response"""
    razorpay_order_id: str
    amount: int  # In paise
    currency: str
    invoice_id: int
    key_id: str


class VerifyPayment(BaseModel):
    """Verify Razorpay payment"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    invoice_id: int


class PaymentResponse(BaseModel):
    """Payment response"""
    id: int
    payment_number: str
    invoice_id: int
    order_id: Optional[int] = None
    amount: float
    payment_method: str
    status: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_date: datetime
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    """Paginated payment list"""
    items: List[PaymentResponse]
    total: int
    page: int
    per_page: int
    pages: int

# Rebuild models for forward references
from app.schemas.user import UserResponse
InvoiceResponse.model_rebuild()
InvoiceListResponse.model_rebuild()


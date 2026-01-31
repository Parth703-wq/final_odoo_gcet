"""
Order Schemas
Pydantic models for order-related API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    """Order status enum for API"""
    QUOTATION = "quotation"
    QUOTATION_SENT = "quotation_sent"
    SALE_ORDER = "sale_order"
    CONFIRMED = "confirmed"
    PICKED_UP = "picked_up"
    ACTIVE = "active"
    RETURNED = "returned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    LATE = "late"


class DeliveryMethodEnum(str, Enum):
    """Delivery method enum"""
    STANDARD = "standard"
    PICKUP = "pickup"


class OrderItemCreate(BaseModel):
    """Create order item"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., ge=1)
    rental_start_date: datetime
    rental_end_date: datetime
    rental_period_type: str = "daily"


class OrderItemUpdate(BaseModel):
    """Update order item"""
    quantity: Optional[int] = Field(None, ge=1)
    rental_start_date: Optional[datetime] = None
    rental_end_date: Optional[datetime] = None


class OrderItemResponse(BaseModel):
    """Order item response"""
    id: int
    product_id: int
    variant_id: Optional[int] = None
    product_name: str
    product_sku: Optional[str] = None
    quantity: int
    unit_price: float
    rental_period_type: str
    rental_start_date: datetime
    rental_end_date: datetime
    line_subtotal: float
    tax_amount: float
    line_total: float
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Create order (quotation) request"""
    items: List[OrderItemCreate]
    rental_start_date: datetime
    rental_end_date: datetime
    delivery_method: DeliveryMethodEnum = DeliveryMethodEnum.STANDARD
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    customer_notes: Optional[str] = None
    discount_code: Optional[str] = None


class OrderUpdate(BaseModel):
    """Update order request"""
    delivery_method: Optional[DeliveryMethodEnum] = None
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    customer_notes: Optional[str] = None
    discount_code: Optional[str] = None


class OrderResponse(BaseModel):
    """Order response"""
    id: int
    order_number: str
    customer_id: int
    vendor_id: int
    status: str
    rental_start_date: datetime
    rental_end_date: datetime
    delivery_method: str
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_charges: float
    subtotal: float
    tax_amount: float
    tax_rate: float
    discount_amount: float
    discount_code: Optional[str] = None
    security_deposit: float
    total_amount: float
    downpayment_amount: float
    downpayment_paid: bool
    late_fees_applied: float
    customer_notes: Optional[str] = None
    order_date: datetime
    confirmed_at: Optional[datetime] = None
    pickup_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Paginated order list"""
    items: List[OrderResponse]
    total: int
    page: int
    per_page: int
    pages: int


class OrderConfirm(BaseModel):
    """Confirm order (convert quotation to sale order)"""
    downpayment_amount: Optional[float] = None
    billing_address: str
    delivery_address: str
    terms_accepted: bool = True


class OrderStatusUpdate(BaseModel):
    """Update order status"""
    status: OrderStatusEnum
    notes: Optional[str] = None


class PickupConfirm(BaseModel):
    """Confirm pickup"""
    picked_up_by: Optional[str] = None
    notes: Optional[str] = None


class ReturnConfirm(BaseModel):
    """Confirm return"""
    received_by: Optional[str] = None
    condition_notes: Optional[str] = None
    damage_reported: bool = False
    damage_description: Optional[str] = None


class AddToCartRequest(BaseModel):
    """Add product to cart (create/update quotation)"""
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., ge=1)
    rental_start_date: datetime
    rental_end_date: datetime
    rental_period_type: str = "daily"


class CartResponse(BaseModel):
    """Shopping cart (quotation) response"""
    order: Optional[OrderResponse] = None
    item_count: int = 0
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0


from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, List
from app.models.payment import PaymentStatus, PaymentMethod

class PaymentBase(BaseModel):
    amount: float
    order_id: Optional[int] = None
    invoice_id: Optional[int] = None
    payment_method: PaymentMethod = PaymentMethod.RAZORPAY

class PaymentCreate(PaymentBase):
    pass

class RazorpayOrderCreate(BaseModel):
    amount: float
    order_id: Optional[int] = None
    invoice_id: Optional[int] = None

class RazorpayOrderResponse(BaseModel):
    razorpay_order_id: str
    amount: float
    currency: str = "INR"
    receipt: str
    key_id: str

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    order_id: Optional[int] = None
    invoice_id: Optional[int] = None

class PaymentResponse(BaseModel):
    id: int
    payment_number: Optional[str] = None
    invoice_id: int
    order_id: Optional[int] = None
    amount: float
    status: PaymentStatus
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

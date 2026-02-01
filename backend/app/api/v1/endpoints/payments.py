<<<<<<< HEAD

=======
"""
Payments API Router - Razorpay Integration
"""
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
<<<<<<< HEAD
=======
from app.models.invoice import Payment
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
from app.schemas.payment import (
    RazorpayOrderCreate, 
    RazorpayOrderResponse, 
    PaymentVerify, 
    PaymentResponse
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

<<<<<<< HEAD
=======

>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
@router.post("/razorpay/order", response_model=RazorpayOrderResponse)
async def create_razorpay_order(
    order_in: RazorpayOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new Razorpay order for payment initiation"""
    payment_service = PaymentService(db)
    try:
        order_data = payment_service.create_razorpay_order(
            customer_id=current_user.id,
            amount=order_in.amount,
            order_id=order_in.order_id,
            invoice_id=order_in.invoice_id
        )
        return order_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

<<<<<<< HEAD
=======

>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
@router.post("/razorpay/verify", response_model=PaymentResponse)
async def verify_payment(
    verify_in: PaymentVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Verify Razorpay payment signature and complete the transaction"""
    payment_service = PaymentService(db)
    payment = payment_service.complete_payment(
        razorpay_order_id=verify_in.razorpay_order_id,
        razorpay_payment_id=verify_in.razorpay_payment_id,
        razorpay_signature=verify_in.razorpay_signature
    )
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found"
        )
        
    if payment.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment verification failed: {payment.failure_reason}"
        )
        
    return payment

<<<<<<< HEAD
=======

>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all payments made by the current user"""
<<<<<<< HEAD
    from app.models.payment import Payment
=======
>>>>>>> aaa4283 (Complete Order Invoice flow, PDF generation fixes, and system-wide improvements)
    payments = db.query(Payment).filter(Payment.customer_id == current_user.id).all()
    return payments

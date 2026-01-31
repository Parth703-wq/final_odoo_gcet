"""
Invoice & Payment API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_vendor
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import (
    InvoiceCreate, InvoiceResponse, InvoiceListResponse,
    CreateRazorpayOrder, RazorpayOrderResponse, VerifyPayment,
    PaymentResponse, PaymentListResponse
)
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Create invoice from order (Vendor only)"""
    service = InvoiceService(db)
    
    try:
        invoice = service.create_invoice_from_order(data.order_id, notes=data.notes)
        return InvoiceResponse.model_validate(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=InvoiceListResponse)
async def get_invoices(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoices based on role"""
    service = InvoiceService(db)
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    if current_user.role.value == "customer":
        result = service.get_invoices(
            customer_id=current_user.id,
            status=status,
            start_date=start,
            end_date=end,
            page=page,
            per_page=per_page
        )
    elif current_user.role.value == "vendor":
        result = service.get_invoices(
            vendor_id=current_user.id,
            status=status,
            start_date=start,
            end_date=end,
            page=page,
            per_page=per_page
        )
    else:  # admin
        result = service.get_invoices(
            status=status,
            start_date=start,
            end_date=end,
            page=page,
            per_page=per_page
        )
    
    return InvoiceListResponse(**result)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice by ID"""
    service = InvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    
    # Check access
    if current_user.role.value == "customer" and invoice.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if current_user.role.value == "vendor" and invoice.vendor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return InvoiceResponse.model_validate(invoice)


@router.post("/{invoice_id}/post", response_model=InvoiceResponse)
async def post_invoice(
    invoice_id: int,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Post invoice (make it official)"""
    service = InvoiceService(db)
    
    try:
        invoice = service.post_invoice(invoice_id)
        return InvoiceResponse.model_validate(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Payment Routes

@router.post("/payments/create-order", response_model=RazorpayOrderResponse)
async def create_payment_order(
    data: CreateRazorpayOrder,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Razorpay order for payment"""
    service = InvoiceService(db)
    
    try:
        result = service.create_razorpay_order(data.invoice_id, data.amount)
        return RazorpayOrderResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/payments/verify", response_model=PaymentResponse)
async def verify_payment(
    data: VerifyPayment,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify Razorpay payment"""
    service = InvoiceService(db)
    
    try:
        payment = service.verify_razorpay_payment(
            data.razorpay_order_id,
            data.razorpay_payment_id,
            data.razorpay_signature,
            data.invoice_id
        )
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/payments/cash", response_model=PaymentResponse)
async def record_cash_payment(
    invoice_id: int,
    amount: float,
    notes: Optional[str] = None,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Record cash payment (Vendor only)"""
    service = InvoiceService(db)
    
    try:
        payment = service.record_cash_payment(invoice_id, amount, notes)
        return PaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/payments/list", response_model=PaymentListResponse)
async def get_payments(
    invoice_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payments"""
    service = InvoiceService(db)
    result = service.get_payments(
        invoice_id=invoice_id,
        status=status,
        page=page,
        per_page=per_page
    )
    
    return PaymentListResponse(**result)

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create invoice from order"""
    service = InvoiceService(db)
    from app.services.order_service import OrderService
    order_service = OrderService(db)
    
    order = order_service.get_order(data.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    # Check if authorized (vendor of order, or customer owner, or admin)
    if current_user.id != order.vendor_id and current_user.id != order.customer_id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create invoice for this order")
    
    try:
        invoice = service.create_invoice_from_order(data.order_id, notes=data.notes)
        return InvoiceResponse.model_validate(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        with open("backend_error.log", "a") as f:
            f.write(f"\n--- Error at {datetime.now()} ---\n")
            f.write(traceback.format_exc())
            f.write("\n")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice by ID with production security and fail-safe data packing"""
    from app.models.invoice import Invoice, InvoiceItem
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Check access (Admin, or Customer/Vendor who owns it)
    is_admin = current_user.role.value == "admin"
    is_owner = current_user.id == invoice.customer_id or current_user.id == invoice.vendor_id
    if not (is_admin or is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this invoice")
        
    # Get items directly
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).all()
    print(f"DEBUG: Found {len(items)} items for Invoice {invoice_id} in GET request")
    
    items_list = []
    for item in items:
        pack = {
            "id": int(item.id),
            "product_name": str(item.product_name),
            "product_sku": str(item.product_sku or ""),
            "description": str(item.description or ""),
            "rental_start_date": item.rental_start_date.isoformat() if item.rental_start_date else None,
            "rental_end_date": item.rental_end_date.isoformat() if item.rental_end_date else None,
            "quantity": int(item.quantity or 1),
            "unit": str(item.unit or "Units"),
            "unit_price": float(item.unit_price or 0.0),
            "tax_rate": float(item.tax_rate or 18.0),
            "cgst": float(item.cgst or 0.0),
            "sgst": float(item.sgst or 0.0),
            "igst": float(item.igst or 0.0),
            "tax_amount": float(item.tax_amount or 0.0),
            "line_total": float(item.line_total or 0.0)
        }
        items_list.append(pack)
        print(f"DEBUG: Packed item {item.id}: {item.product_name}")
    
    # Build response dict
    response_data = {
        "id": int(invoice.id),
        "invoice_number": str(invoice.invoice_number),
        "order_id": int(invoice.order_id),
        "customer_id": int(invoice.customer_id),
        "vendor_id": int(invoice.vendor_id),
        "status": str(invoice.status.value) if hasattr(invoice.status, 'value') else str(invoice.status),
        "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "rental_start_date": invoice.rental_start_date.isoformat() if invoice.rental_start_date else None,
        "rental_end_date": invoice.rental_end_date.isoformat() if invoice.rental_end_date else None,
        "billing_address": str(invoice.billing_address or ""),
        "delivery_address": str(invoice.delivery_address or ""),
        "vendor_company_name": str(invoice.vendor_company_name or ""),
        "customer_name": str(invoice.customer_name or ""),
        "subtotal": float(invoice.subtotal or 0.0),
        "tax_rate": float(invoice.tax_rate or 18.0),
        "cgst": float(invoice.cgst or 0.0),
        "sgst": float(invoice.sgst or 0.0),
        "igst": float(invoice.igst or 0.0),
        "tax_amount": float(invoice.tax_amount or 0.0),
        "total_amount": float(invoice.total_amount or 0.0),
        "amount_paid": float(invoice.amount_paid or 0.0),
        "amount_due": float(invoice.amount_due or 0.0),
        "notes": str(invoice.notes or ""),
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
        "items": items_list
    }
    
    # CRITICAL: Print JSON to terminal so I can see it in logs
    import json
    print(f"CRITICAL_JSON_OUT: {json.dumps(response_data)}")
    return response_data


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

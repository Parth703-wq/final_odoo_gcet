"""
Order API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_vendor
from app.services.order_service import OrderService
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderConfirm, OrderStatusUpdate, PickupConfirm, ReturnConfirm,
    AddToCartRequest, CartResponse
)
from app.models.user import User

router = APIRouter(prefix="/orders", tags=["Orders"])


# Cart Routes

@router.get("/cart", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart (active quotation)"""
    service = OrderService(db)
    cart = service.get_customer_cart(current_user.id)
    
    if not cart:
        return CartResponse(order=None, item_count=0, subtotal=0, tax_amount=0, total_amount=0)
    
    return CartResponse(
        order=OrderResponse.model_validate(cart),
        item_count=len(cart.items),
        subtotal=cart.subtotal,
        tax_amount=cart.tax_amount,
        total_amount=cart.total_amount
    )


@router.post("/cart/add", response_model=CartResponse)
async def add_to_cart(
    data: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to cart"""
    service = OrderService(db)
    
    try:
        from app.schemas.order import OrderItemCreate
        
        item = OrderItemCreate(
            product_id=data.product_id,
            variant_id=data.variant_id,
            quantity=data.quantity,
            rental_start_date=data.rental_start_date,
            rental_end_date=data.rental_end_date,
            rental_period_type=data.rental_period_type
        )
        
        cart = service.add_to_cart(current_user.id, item)
        
        return CartResponse(
            order=OrderResponse.model_validate(cart),
            item_count=len(cart.items),
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            total_amount=cart.total_amount
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/cart/item/{item_id}", response_model=CartResponse)
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    service = OrderService(db)
    cart = service.remove_from_cart(current_user.id, item_id)
    
    if not cart:
        return CartResponse(order=None, item_count=0, subtotal=0, tax_amount=0, total_amount=0)
    
    return CartResponse(
        order=OrderResponse.model_validate(cart),
        item_count=len(cart.items),
        subtotal=cart.subtotal,
        tax_amount=cart.tax_amount,
        total_amount=cart.total_amount
    )


# Order Routes

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order (quotation)"""
    service = OrderService(db)
    
    try:
        order = service.create_quotation(current_user.id, data)
        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=OrderListResponse)
async def get_orders(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders (customers see their orders, vendors see orders for their products)"""
    service = OrderService(db)
    
    # Parse dates
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    if current_user.role.value == "customer":
        result = service.get_orders(
            customer_id=current_user.id,
            status=status,
            start_date=start,
            end_date=end,
            page=page,
            per_page=per_page
        )
    elif current_user.role.value in ["vendor", "admin"]:
        vendor_id = current_user.id if current_user.role.value == "vendor" else None
        result = service.get_orders(
            vendor_id=vendor_id,
            status=status,
            start_date=start,
            end_date=end,
            page=page,
            per_page=per_page
        )
    else:
        result = {"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0}
    
    return OrderListResponse(**result)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check access
    if current_user.role.value == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if current_user.role.value == "vendor" and order.vendor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int,
    data: OrderConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm quotation and convert to sale order"""
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        confirmed = service.confirm_order(order_id, data)
        
        # Generate Invoice automatically
        try:
            from app.services.invoice_service import InvoiceService
            invoice_service = InvoiceService(db)
            invoice_service.create_invoice_from_order(confirmed.id)
        except Exception as e:
            # Log error but don't fail the order confirmation
            print(f"Failed to generate invoice for order {order_id}: {str(e)}")
            
        return OrderResponse.model_validate(confirmed)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/pickup", response_model=OrderResponse)
async def mark_pickup(
    order_id: int,
    data: PickupConfirm,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Mark order as picked up (Vendor only)"""
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.vendor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        updated = service.mark_picked_up(order_id, data.picked_up_by, data.notes)
        return OrderResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/return", response_model=OrderResponse)
async def mark_return(
    order_id: int,
    data: ReturnConfirm,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Mark order as returned (Vendor only)"""
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.vendor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        updated = service.mark_returned(
            order_id,
            data.received_by,
            data.condition_notes,
            data.damage_reported,
            data.damage_description
        )
        return OrderResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel order"""
    service = OrderService(db)
    order = service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check access
    if current_user.role.value == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        cancelled = service.cancel_order(order_id, notes)
        return OrderResponse.model_validate(cancelled)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Vendor-specific routes

@router.get("/vendor/pending-pickups", response_model=OrderListResponse)
async def get_pending_pickups(
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get orders pending pickup (Vendor only)"""
    service = OrderService(db)
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    orders = service.get_pending_pickups(vendor_id)
    
    return OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=len(orders),
        page=1,
        per_page=100,
        pages=1
    )


@router.get("/vendor/upcoming-returns", response_model=OrderListResponse)
async def get_upcoming_returns(
    days: int = Query(1, ge=1, le=30),
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get orders with upcoming returns (Vendor only)"""
    service = OrderService(db)
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    orders = service.get_upcoming_returns(vendor_id, days)
    
    return OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=len(orders),
        page=1,
        per_page=100,
        pages=1
    )


@router.get("/vendor/overdue", response_model=OrderListResponse)
async def get_overdue_orders(
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get overdue orders (Vendor only)"""
    service = OrderService(db)
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    orders = service.get_overdue_orders(vendor_id)
    
    return OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in orders],
        total=len(orders),
        page=1,
        per_page=100,
        pages=1
    )

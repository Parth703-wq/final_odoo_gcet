"""
Admin & Settings API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.auth_service import AuthService
from app.schemas.user import UserResponse
from app.schemas.common import (
    RentalPeriodConfigCreate, RentalPeriodConfigResponse,
    CompanySettingsUpdate, CompanySettingsResponse,
    CouponCreate, CouponResponse, ApplyCoupon, CouponValidationResponse,
    MessageResponse
)
from app.models.user import User
from app.models.settings import RentalPeriodConfig, CompanySettings, Coupon

router = APIRouter(prefix="/admin", tags=["Admin & Settings"])


# User Management

@router.get("/users")
async def get_users(
    role: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    service = AuthService(db)
    return service.get_all_users(role=role, page=page, per_page=per_page)


@router.post("/users/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate/deactivate user (Admin only)"""
    service = AuthService(db)
    user = service.toggle_user_status(user_id, is_active)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse.model_validate(user)


# Rental Period Configuration

@router.get("/rental-periods", response_model=List[RentalPeriodConfigResponse])
async def get_rental_periods(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get rental period configurations"""
    configs = db.query(RentalPeriodConfig).all()
    return [RentalPeriodConfigResponse.model_validate(c) for c in configs]


@router.post("/rental-periods", response_model=RentalPeriodConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_rental_period(
    data: RentalPeriodConfigCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create rental period configuration"""
    config = RentalPeriodConfig(
        name=data.name,
        duration_type=data.duration_type,
        duration_value=data.duration_value,
        is_active=data.is_active
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return RentalPeriodConfigResponse.model_validate(config)


@router.delete("/rental-periods/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental_period(
    config_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete rental period configuration"""
    config = db.query(RentalPeriodConfig).filter(RentalPeriodConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    
    db.delete(config)
    db.commit()


# Company Settings

@router.get("/settings", response_model=CompanySettingsResponse)
async def get_company_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get company settings"""
    settings = db.query(CompanySettings).first()
    
    if not settings:
        # Create default settings
        settings = CompanySettings(
            company_name="Rental Management System",
            gst_rate=18.0,
            currency_code="INR",
            currency_symbol="₹",
            late_fee_per_day=100.0,
            late_fee_percentage=5.0
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return CompanySettingsResponse.model_validate(settings)


@router.put("/settings", response_model=CompanySettingsResponse)
async def update_company_settings(
    data: CompanySettingsUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update company settings"""
    settings = db.query(CompanySettings).first()
    
    if not settings:
        settings = CompanySettings()
        db.add(settings)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    
    return CompanySettingsResponse.model_validate(settings)


# Coupons

@router.get("/coupons", response_model=List[CouponResponse])
async def get_coupons(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all coupons"""
    coupons = db.query(Coupon).all()
    return [CouponResponse.model_validate(c) for c in coupons]


@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    data: CouponCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create coupon"""
    # Check if code exists
    existing = db.query(Coupon).filter(Coupon.code == data.code.upper()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon code already exists")
    
    coupon = Coupon(
        code=data.code.upper(),
        description=data.description,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        max_discount=data.max_discount,
        min_order_value=data.min_order_value,
        usage_limit=data.usage_limit,
        per_user_limit=data.per_user_limit,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        is_active=data.is_active
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    
    return CouponResponse.model_validate(coupon)


@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete coupon"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    
    db.delete(coupon)
    db.commit()


@router.post("/coupons/validate", response_model=CouponValidationResponse)
async def validate_coupon(
    data: ApplyCoupon,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate and calculate coupon discount"""
    from datetime import datetime
    
    coupon = db.query(Coupon).filter(
        Coupon.code == data.code.upper(),
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        return CouponValidationResponse(is_valid=False, discount_amount=0, message="Invalid coupon code")
    
    # Check validity period
    now = datetime.utcnow()
    if coupon.valid_from and now < coupon.valid_from:
        return CouponValidationResponse(is_valid=False, discount_amount=0, message="Coupon not yet active")
    
    if coupon.valid_until and now > coupon.valid_until:
        return CouponValidationResponse(is_valid=False, discount_amount=0, message="Coupon expired")
    
    # Check usage limit
    if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
        return CouponValidationResponse(is_valid=False, discount_amount=0, message="Coupon usage limit reached")
    
    # Check minimum order value
    if data.order_total < coupon.min_order_value:
        return CouponValidationResponse(
            is_valid=False,
            discount_amount=0,
            message=f"Minimum order value is ₹{coupon.min_order_value}"
        )
    
    # Calculate discount
    if coupon.discount_type == "percentage":
        discount = data.order_total * (coupon.discount_value / 100)
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value
    
    return CouponValidationResponse(
        is_valid=True,
        discount_amount=discount,
        message=f"Coupon applied! You save ₹{discount:.2f}"
    )


# Export Endpoints

@router.get("/export/orders")
async def export_orders(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Export orders as CSV"""
    from fastapi.responses import PlainTextResponse
    from app.models.order import Order
    
    orders = db.query(Order).all()
    
    # Build CSV
    lines = ["Order Number,Customer ID,Vendor ID,Status,Total Amount,Order Date"]
    for o in orders:
        lines.append(f"{o.order_number},{o.customer_id},{o.vendor_id},{o.status},{o.total_amount},{o.order_date}")
    
    return PlainTextResponse(content="\n".join(lines), media_type="text/csv")


@router.get("/export/invoices")
async def export_invoices(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Export invoices as CSV"""
    from fastapi.responses import PlainTextResponse
    from app.models.invoice import Invoice
    
    invoices = db.query(Invoice).all()
    
    # Build CSV
    lines = ["Invoice Number,Order ID,Status,Amount Due,Amount Paid,Due Date"]
    for inv in invoices:
        lines.append(f"{inv.invoice_number},{inv.order_id},{inv.status},{inv.amount_due},{inv.amount_paid},{inv.due_date}")
    
    return PlainTextResponse(content="\n".join(lines), media_type="text/csv")

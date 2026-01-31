"""
Common Schemas and Settings Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Common Response Schemas

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


# Settings Schemas

class RentalPeriodConfigCreate(BaseModel):
    """Create rental period config"""
    name: str = Field(..., min_length=1, max_length=100)
    duration_type: str  # hour, day, week, month
    duration_value: int = 1
    is_active: bool = True


class RentalPeriodConfigResponse(RentalPeriodConfigCreate):
    """Rental period config response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompanySettingsUpdate(BaseModel):
    """Update company settings"""
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    company_email: Optional[str] = None
    company_website: Optional[str] = None
    gstin: Optional[str] = None
    gst_rate: Optional[float] = None
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    late_fee_per_day: Optional[float] = None
    late_fee_percentage: Optional[float] = None
    default_terms_conditions: Optional[str] = None


class CompanySettingsResponse(BaseModel):
    """Company settings response"""
    id: int
    company_name: str
    company_logo: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    company_email: Optional[str] = None
    company_website: Optional[str] = None
    gstin: Optional[str] = None
    gst_rate: float
    currency_code: str
    currency_symbol: str
    late_fee_per_day: float
    late_fee_percentage: float
    default_terms_conditions: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Coupon Schemas

class CouponCreate(BaseModel):
    """Create coupon"""
    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    discount_type: str = "percentage"  # percentage, fixed
    discount_value: float = Field(..., gt=0)
    max_discount: Optional[float] = None
    min_order_value: float = 0.0
    usage_limit: Optional[int] = None
    per_user_limit: int = 1
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True


class CouponResponse(CouponCreate):
    """Coupon response"""
    id: int
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApplyCoupon(BaseModel):
    """Apply coupon to order"""
    code: str
    order_total: float


class CouponValidationResponse(BaseModel):
    """Coupon validation response"""
    is_valid: bool
    discount_amount: float = 0.0
    message: str


# Notification Schemas

class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    title: str
    message: str
    notification_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list"""
    items: List[NotificationResponse]
    unread_count: int


# Dashboard & Reports Schemas

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_revenue: float
    total_orders: int
    active_rentals: int
    pending_returns: int
    overdue_returns: int
    total_customers: int
    total_products: int


class VendorDashboardStats(DashboardStats):
    """Vendor-specific dashboard"""
    today_revenue: float
    week_revenue: float
    month_revenue: float
    pending_pickups: int


class AdminDashboardStats(DashboardStats):
    """Admin dashboard"""
    total_vendors: int
    total_revenue_today: float
    total_revenue_week: float
    total_revenue_month: float


class RevenueChartData(BaseModel):
    """Revenue chart data point"""
    date: str
    revenue: float


class TopProductData(BaseModel):
    """Top rented product data"""
    product_id: int
    product_name: str
    rental_count: int
    revenue: float


class VendorPerformanceData(BaseModel):
    """Vendor performance data"""
    vendor_id: int
    vendor_name: str
    total_orders: int
    total_revenue: float
    rating: Optional[float] = None


class ReportFilters(BaseModel):
    """Report filter parameters"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    vendor_id: Optional[int] = None
    status: Optional[str] = None
    export_format: Optional[str] = "csv"  # csv, xlsx, pdf

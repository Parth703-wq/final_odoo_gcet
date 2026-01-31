"""
Schemas Package
Exports all Pydantic schemas
"""

from app.schemas.user import (
    CustomerSignup, VendorSignup, UserLogin, 
    ForgotPassword, ResetPassword, ChangePassword,
    UserUpdate, UserResponse, TokenResponse
)
from app.schemas.product import (
    CategoryCreate, CategoryResponse,
    ProductAttributeCreate, ProductAttributeResponse,
    ProductVariantCreate, ProductVariantResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductAvailabilityCheck, ProductAvailabilityResponse
)
from app.schemas.order import (
    OrderItemCreate, OrderItemUpdate, OrderItemResponse,
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderConfirm, OrderStatusUpdate, PickupConfirm, ReturnConfirm,
    AddToCartRequest, CartResponse, OrderStatusEnum, DeliveryMethodEnum
)
from app.schemas.invoice import (
    InvoiceItemCreate, InvoiceItemResponse,
    InvoiceCreate, InvoiceResponse, InvoiceListResponse,
    CreateRazorpayOrder, RazorpayOrderResponse, VerifyPayment,
    PaymentResponse, PaymentListResponse,
    InvoiceStatusEnum, PaymentMethodEnum
)
from app.schemas.common import (
    MessageResponse, ErrorResponse, PaginationParams,
    RentalPeriodConfigCreate, RentalPeriodConfigResponse,
    CompanySettingsUpdate, CompanySettingsResponse,
    CouponCreate, CouponResponse, ApplyCoupon, CouponValidationResponse,
    NotificationResponse, NotificationListResponse,
    DashboardStats, VendorDashboardStats, AdminDashboardStats,
    RevenueChartData, TopProductData, VendorPerformanceData, ReportFilters
)

__all__ = [
    # User
    "CustomerSignup", "VendorSignup", "UserLogin",
    "ForgotPassword", "ResetPassword", "ChangePassword",
    "UserUpdate", "UserResponse", "TokenResponse",
    
    # Product
    "CategoryCreate", "CategoryResponse",
    "ProductAttributeCreate", "ProductAttributeResponse",
    "ProductVariantCreate", "ProductVariantResponse",
    "ProductCreate", "ProductUpdate", "ProductResponse", "ProductListResponse",
    "ProductAvailabilityCheck", "ProductAvailabilityResponse",
    
    # Order
    "OrderItemCreate", "OrderItemUpdate", "OrderItemResponse",
    "OrderCreate", "OrderUpdate", "OrderResponse", "OrderListResponse",
    "OrderConfirm", "OrderStatusUpdate", "PickupConfirm", "ReturnConfirm",
    "AddToCartRequest", "CartResponse", "OrderStatusEnum", "DeliveryMethodEnum",
    
    # Invoice
    "InvoiceItemCreate", "InvoiceItemResponse",
    "InvoiceCreate", "InvoiceResponse", "InvoiceListResponse",
    "CreateRazorpayOrder", "RazorpayOrderResponse", "VerifyPayment",
    "PaymentResponse", "PaymentListResponse",
    "InvoiceStatusEnum", "PaymentMethodEnum",
    
    # Common
    "MessageResponse", "ErrorResponse", "PaginationParams",
    "RentalPeriodConfigCreate", "RentalPeriodConfigResponse",
    "CompanySettingsUpdate", "CompanySettingsResponse",
    "CouponCreate", "CouponResponse", "ApplyCoupon", "CouponValidationResponse",
    "NotificationResponse", "NotificationListResponse",
    "DashboardStats", "VendorDashboardStats", "AdminDashboardStats",
    "RevenueChartData", "TopProductData", "VendorPerformanceData", "ReportFilters",
]

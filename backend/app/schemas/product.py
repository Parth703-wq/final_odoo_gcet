"""
Product Schemas
Pydantic models for product-related API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    image_url: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Create category request"""
    pass


class CategoryResponse(CategoryBase):
    """Category response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductAttributeCreate(BaseModel):
    """Create product attribute"""
    name: str = Field(..., min_length=1, max_length=100)
    values: List[str] = []


class ProductAttributeResponse(ProductAttributeCreate):
    """Product attribute response"""
    id: int
    
    class Config:
        from_attributes = True


class ProductVariantCreate(BaseModel):
    """Create product variant"""
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = None
    attributes: Dict[str, Any] = {}
    rental_price_hourly: Optional[float] = None
    rental_price_daily: Optional[float] = None
    rental_price_weekly: Optional[float] = None
    rental_price_monthly: Optional[float] = None
    quantity_on_hand: int = 0


class ProductVariantResponse(ProductVariantCreate):
    """Product variant response"""
    id: int
    quantity_reserved: int = 0
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    gallery_images: List[str] = []
    
    # Pricing
    cost_price: float = 0.0
    sales_price: float = 0.0
    
    # Rental Pricing
    rental_price_hourly: float = 0.0
    rental_price_daily: float = 0.0
    rental_price_weekly: float = 0.0
    rental_price_monthly: float = 0.0
    
    # Security Deposit
    security_deposit: float = 0.0
    
    # Inventory
    quantity_on_hand: int = 0
    
    # Category & Attributes
    category_id: Optional[int] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    attributes: Dict[str, Any] = {}


class ProductCreate(ProductBase):
    """Create product request"""
    is_rentable: bool = True
    is_published: bool = False
    variants: List[ProductVariantCreate] = []


class ProductUpdate(BaseModel):
    """Update product request"""
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    cost_price: Optional[float] = None
    sales_price: Optional[float] = None
    rental_price_hourly: Optional[float] = None
    rental_price_daily: Optional[float] = None
    rental_price_weekly: Optional[float] = None
    rental_price_monthly: Optional[float] = None
    security_deposit: Optional[float] = None
    quantity_on_hand: Optional[int] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    is_rentable: Optional[bool] = None
    is_published: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response"""
    id: int
    vendor_id: int
    quantity_reserved: int = 0
    is_rentable: bool
    is_published: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    variants: List[ProductVariantResponse] = []
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Paginated product list response"""
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ProductAvailabilityCheck(BaseModel):
    """Check product availability for date range"""
    product_id: int
    variant_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    quantity: int = 1


class ProductAvailabilityResponse(BaseModel):
    """Product availability response"""
    product_id: int
    variant_id: Optional[int] = None
    is_available: bool
    available_quantity: int
    requested_quantity: int
    start_date: datetime
    end_date: datetime
    conflicts: List[Dict[str, Any]] = []

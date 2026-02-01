"""
Product API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import shutil
import os

from app.core.database import get_db
from app.core.security import get_current_user, require_vendor, require_admin
from app.services.product_service import ProductService
from app.schemas.product import (
    CategoryCreate, CategoryResponse,
    ProductAttributeCreate, ProductAttributeResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductAvailabilityCheck, ProductAvailabilityResponse
)
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/upload-image")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_vendor)
):
    """Upload product image"""
    # Create directory if it doesn't exist
    upload_path = os.path.join("uploads", "products")
    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_path, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return relative URL for static mounting
    url = f"/uploads/products/{filename}"
    return {"url": url}


# Category Routes

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    service = ProductService(db)
    return service.get_categories()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new category (Admin only)"""
    service = ProductService(db)
    return service.create_category(
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
        image_url=data.image_url
    )


# Product Attribute Routes

@router.get("/attributes", response_model=List[ProductAttributeResponse])
async def get_attributes(db: Session = Depends(get_db)):
    """Get all product attributes"""
    service = ProductService(db)
    return service.get_attributes()


@router.post("/attributes", response_model=ProductAttributeResponse, status_code=status.HTTP_201_CREATED)
async def create_attribute(
    data: ProductAttributeCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new product attribute (Admin only)"""
    service = ProductService(db)
    return service.create_attribute(name=data.name, values=data.values)


# Product Routes

@router.get("", response_model=ProductListResponse)
async def get_products(
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    color: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get published products (public)"""
    service = ProductService(db)
    result = service.get_products(
        is_published=True,
        is_rentable=True,
        category_id=category_id,
        brand=brand,
        color=color,
        min_price=min_price,
        max_price=max_price,
        search=search,
        page=page,
        per_page=per_page
    )
    return ProductListResponse(**result)


@router.get("/vendor", response_model=ProductListResponse)
async def get_vendor_products(
    is_published: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get vendor's own products"""
    service = ProductService(db)
    result = service.get_products(
        vendor_id=current_user.id,
        is_published=is_published,
        search=search,
        page=page,
        per_page=per_page
    )
    return ProductListResponse(**result)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    service = ProductService(db)
    product = service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Create a new product (Vendor only)"""
    service = ProductService(db)
    product = service.create_product(vendor_id=current_user.id, data=data)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Update product (Owner only)"""
    service = ProductService(db)
    product = service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.vendor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    updated = service.update_product(product_id, data)
    return ProductResponse.model_validate(updated)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Delete product (Owner only)"""
    service = ProductService(db)
    product = service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.vendor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    service.delete_product(product_id)


@router.post("/{product_id}/toggle-publish", response_model=ProductResponse)
async def toggle_publish(
    product_id: int,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Toggle product publish status"""
    service = ProductService(db)
    product = service.get_product(product_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.vendor_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    updated = service.toggle_publish(product_id)
    return ProductResponse.model_validate(updated)


# Availability Routes

@router.post("/check-availability", response_model=ProductAvailabilityResponse)
async def check_availability(
    data: ProductAvailabilityCheck,
    db: Session = Depends(get_db)
):
    """Check product availability for date range"""
    service = ProductService(db)
    result = service.check_availability(
        product_id=data.product_id,
        start_date=data.start_date,
        end_date=data.end_date,
        quantity=data.quantity,
        variant_id=data.variant_id
    )
    return ProductAvailabilityResponse(**result)


@router.get("/{product_id}/availability-calendar")
async def get_availability_calendar(
    product_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """Get product availability calendar"""
    from datetime import datetime
    
    service = ProductService(db)
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    return service.get_availability_calendar(product_id, start, end)

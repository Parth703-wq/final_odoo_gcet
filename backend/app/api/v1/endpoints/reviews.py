from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.review import Review
from app.models.order import Order, OrderStatus
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewList

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("", response_model=ReviewResponse)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product review"""
    # Check if order exists and belongs to customer
    order = db.query(Order).filter(Order.id == data.order_id, Order.customer_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if order is in valid status (picked_up or active)
    if order.status not in [OrderStatus.PICKED_UP, OrderStatus.ACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Reviews can only be left after receiving delivery and before returning"
        )
    
    # Check if already reviewed for this product in this order
    existing = db.query(Review).filter(
        Review.order_id == data.order_id, 
        Review.product_id == data.product_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review already exists")
    
    review = Review(
        product_id=data.product_id,
        customer_id=current_user.id,
        order_id=data.order_id,
        rating=data.rating,
        comment=data.comment
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Attach customer name for response
    response = ReviewResponse.model_validate(review)
    response.customer_name = f"{current_user.first_name} {current_user.last_name}"
    
    return response

@router.get("/product/{product_id}", response_model=ReviewList)
async def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all reviews for a product"""
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    
    items = []
    for r in reviews:
        res = ReviewResponse.model_validate(r)
        if r.customer:
            res.customer_name = f"{r.customer.first_name} {r.customer.last_name}"
        items.append(res)
        
    return ReviewList(items=items, total=len(items))

@router.get("/order/{order_id}", response_model=ReviewList)
async def get_order_reviews(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reviews for a specific order (for visibility to customer/vendor)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Permission check
    if current_user.role.value == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if current_user.role.value == "vendor" and order.vendor_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    reviews = db.query(Review).filter(Review.order_id == order_id).all()
    
    items = []
    for r in reviews:
        res = ReviewResponse.model_validate(r)
        if r.customer:
            res.customer_name = f"{r.customer.first_name} {r.customer.last_name}"
        items.append(res)
        
    return ReviewList(items=items, total=len(items))

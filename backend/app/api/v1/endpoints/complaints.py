from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.complaint import Complaint
from app.models.order import Order
from app.models.product import Product
from app.schemas.complaint import ComplaintCreate, ComplaintResponse, ComplaintList, ComplaintUpdate

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("", response_model=ComplaintResponse)
async def create_complaint(
    data: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customer creates a complaint"""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can file complaints")
        
    # Verify order belongs to customer
    order = db.query(Order).filter(Order.id == data.order_id, Order.customer_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check if order is in valid status for complaint (must have received product)
    # Import OrderStatus here or from app.models.order
    from app.models.order import OrderStatus
    if order.status not in [OrderStatus.PICKED_UP, OrderStatus.ACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Complaints can only be filed while the item is in your possession (after pickup/delivery)."
        )

    complaint = Complaint(
        order_id=data.order_id,
        product_id=data.product_id,
        customer_id=current_user.id,
        subject=data.subject,
        description=data.description
    )
    
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

@router.get("", response_model=ComplaintList)
async def list_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List complaints - Admin sees all, Customer sees their own, Vendor sees NONE"""
    query = db.query(Complaint)
    
    if current_user.role == UserRole.ADMIN:
        # Admin sees everything
        pass
    elif current_user.role == UserRole.CUSTOMER:
        query = query.filter(Complaint.customer_id == current_user.id)
    else:
        # Vendors are blocked from seeing complaints
        raise HTTPException(status_code=403, detail="Vendors do not have access to complaints")
        
    complaints = query.order_by(Complaint.created_at.desc()).all()
    
    results = []
    for c in complaints:
        res = ComplaintResponse.model_validate(c)
        res.customer_name = f"{c.customer.first_name} {c.customer.last_name}"
        res.product_name = c.product.name
        res.order_number = c.order.order_number
        results.append(res)
        
    return ComplaintList(items=results, total=len(results))

@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    data: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin updates complaint status and notes"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can update complaints")
        
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    if data.status:
        complaint.status = data.status
        if data.status == "resolved":
            from datetime import datetime
            complaint.resolved_at = datetime.utcnow()
            
    if data.admin_notes is not None:
        complaint.admin_notes = data.admin_notes
        
    db.commit()
    db.refresh(complaint)
    return complaint

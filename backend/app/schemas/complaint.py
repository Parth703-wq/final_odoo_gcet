from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.complaint import ComplaintStatus

class ComplaintBase(BaseModel):
    order_id: int
    product_id: int
    subject: str
    description: str

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    admin_notes: Optional[str] = None

class ComplaintResponse(ComplaintBase):
    id: int
    customer_id: int
    status: ComplaintStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    # Extra info for admin
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    order_number: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ComplaintList(BaseModel):
    items: List[ComplaintResponse]
    total: int

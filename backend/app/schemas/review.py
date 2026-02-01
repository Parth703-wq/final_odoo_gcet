from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

class ReviewBase(BaseModel):
    product_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: int
    customer_id: int
    created_at: datetime
    
    # Optional nested data
    customer_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ReviewList(BaseModel):
    items: List[ReviewResponse]
    total: int

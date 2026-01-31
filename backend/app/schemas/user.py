"""
User Schemas
Pydantic models for user-related API requests/responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class CustomerSignup(UserBase):
    """Customer signup request"""
    password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str
    phone: Optional[str] = None
    coupon_code: Optional[str] = None
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class VendorSignup(CustomerSignup):
    """Vendor signup request"""
    company_name: str = Field(..., min_length=1, max_length=255)
    gstin: str = Field(..., min_length=15, max_length=15)
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    @validator('gstin')
    def validate_gstin(cls, v):
        """Validate GSTIN format: 2 digits + 10 chars + 1 digit + 1 char + 1 digit"""
        gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(gstin_pattern, v.upper()):
            raise ValueError('Invalid GSTIN format')
        return v.upper()


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class ForgotPassword(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPassword(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class ChangePassword(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseModel):
    """User profile update"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    gstin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None


class UserResponse(UserBase):
    """User response"""
    id: int
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    gstin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

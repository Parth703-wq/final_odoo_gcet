"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import (
    CustomerSignup, VendorSignup, UserLogin,
    ForgotPassword, ResetPassword, ChangePassword,
    UserUpdate, UserResponse, TokenResponse
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup/customer", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def customer_signup(data: CustomerSignup, db: Session = Depends(get_db)):
    """Register a new customer"""
    service = AuthService(db)
    
    try:
        user = service.create_customer(data)
        token = service.create_user_token(user)
        
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/signup/vendor", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def vendor_signup(data: VendorSignup, db: Session = Depends(get_db)):
    """Register a new vendor"""
    service = AuthService(db)
    
    try:
        user = service.create_vendor(data)
        token = service.create_user_token(user)
        
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    service = AuthService(db)
    
    user = service.authenticate_user(data.email, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = service.create_user_token(user)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    """Request password reset"""
    service = AuthService(db)
    
    # Always return success to prevent email enumeration
    service.generate_password_reset_token(data.email)
    
    return MessageResponse(
        message="If an account exists with this email, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """Reset password with token"""
    service = AuthService(db)
    
    success = service.reset_password(data.token, data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return MessageResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePassword,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for logged in user"""
    service = AuthService(db)
    
    success = service.change_password(current_user, data.current_password, data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return MessageResponse(message="Password changed successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    service = AuthService(db)
    
    updated_user = service.update_user_profile(current_user, data.model_dump(exclude_unset=True))
    
    return UserResponse.model_validate(updated_user)

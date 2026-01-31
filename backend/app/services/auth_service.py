"""
Authentication Service
Handles user registration, login, and password management
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import CustomerSignup, VendorSignup, UserLogin, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.email_service import send_password_reset_email


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_customer(self, data: CustomerSignup) -> User:
        """Create a new customer"""
        # Check if email exists
        if self.get_user_by_email(data.email):
            raise ValueError("Email already registered")
        
        user = User(
            email=data.email.lower(),
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=UserRole.CUSTOMER,
            coupon_code_used=data.coupon_code,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_vendor(self, data: VendorSignup) -> User:
        """Create a new vendor"""
        # Check if email exists
        if self.get_user_by_email(data.email):
            raise ValueError("Email already registered")
        
        user = User(
            email=data.email.lower(),
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            company_name=data.company_name,
            gstin=data.gstin,
            address_line1=data.address_line1,
            city=data.city,
            state=data.state,
            zip_code=data.zip_code,
            role=UserRole.VENDOR,
            coupon_code_used=data.coupon_code,
            is_active=True,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_user_token(self, user: User) -> str:
        """Create JWT token for user"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        return create_access_token(token_data)
    
    def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generate password reset token"""
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        # Generate token
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        self.db.commit()
        
        # Send email
        send_password_reset_email(user.email, token)
        
        return token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        user = self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        self.db.commit()
        
        return True
    
    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password"""
        if not verify_password(current_password, user.password_hash):
            return False
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        return True
    
    def update_user_profile(self, user: User, data: dict) -> User:
        """Update user profile"""
        for key, value in data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_all_users(self, role: Optional[str] = None, page: int = 1, per_page: int = 20):
        """Get all users with pagination"""
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "items": users,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    
    def toggle_user_status(self, user_id: int, is_active: bool) -> Optional[User]:
        """Activate or deactivate user"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            return None
        
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        
        return user

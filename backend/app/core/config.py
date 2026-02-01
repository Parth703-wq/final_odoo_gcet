"""
Core Configuration Module
Loads environment variables and provides settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application Settings"""
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "rental_management_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Razorpay
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Rental Management System")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Database Toggle
    USE_SQLITE: str = os.getenv("USE_SQLITE", "true")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL with SQLite fallback"""
        use_sqlite = self.USE_SQLITE.lower() == "true"
        if use_sqlite:
            return "sqlite:///./rental_management.db"
            
        if self.DB_PASSWORD:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"mysql+pymysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


def get_settings() -> Settings:
    """Get settings instance (no caching to pick up env changes)"""
    return Settings()


settings = get_settings()

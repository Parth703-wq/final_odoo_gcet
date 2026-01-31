"""
Rental Management System - FastAPI Backend
Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router

# Import all models so they are registered with SQLAlchemy
from app.models import (
    User, UserRole,
    Product, ProductVariant, Category, ProductAttribute,
    Order, OrderItem, OrderStatus,
    Invoice, InvoiceItem, Payment,
    Reservation, PickupDocument, ReturnDocument,
    RentalPeriodConfig, CompanySettings, Coupon, Notification
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - creates tables on startup"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title=settings.APP_NAME,
    description="Rental Management System - Complete ERP for rental businesses",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Rental Management System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

"""
Dashboard & Reports API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, require_vendor, require_admin
from app.services.dashboard_service import DashboardService
from app.schemas.common import (
    DashboardStats, VendorDashboardStats, AdminDashboardStats,
    RevenueChartData, TopProductData, VendorPerformanceData
)
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Reports"])


@router.get("/admin", response_model=AdminDashboardStats)
async def get_admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    service = DashboardService(db)
    return service.get_admin_dashboard()


@router.get("/vendor", response_model=VendorDashboardStats)
async def get_vendor_dashboard(
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get vendor dashboard statistics"""
    service = DashboardService(db)
    
    if current_user.role.value == "admin":
        # Admin can see all vendors' combined stats
        return service.get_admin_dashboard()
    
    return service.get_vendor_dashboard(current_user.id)


@router.get("/revenue-chart")
async def get_revenue_chart(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get revenue chart data"""
    service = DashboardService(db)
    
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    
    return service.get_revenue_chart(vendor_id=vendor_id, days=days)


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Get most rented products"""
    service = DashboardService(db)
    
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    
    return service.get_top_products(vendor_id=vendor_id, limit=limit)


@router.get("/vendor-performance")
async def get_vendor_performance(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get vendor performance data (Admin only)"""
    service = DashboardService(db)
    return service.get_vendor_performance(limit=limit)


# Export Routes

@router.get("/export/orders")
async def export_orders(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Export orders to CSV"""
    service = DashboardService(db)
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    
    csv_content = service.export_orders_csv(
        vendor_id=vendor_id,
        start_date=start,
        end_date=end
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )


@router.get("/export/invoices")
async def export_invoices(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_vendor),
    db: Session = Depends(get_db)
):
    """Export invoices to CSV"""
    service = DashboardService(db)
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    vendor_id = None if current_user.role.value == "admin" else current_user.id
    
    csv_content = service.export_invoices_csv(
        vendor_id=vendor_id,
        start_date=start,
        end_date=end
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=invoices_export.csv"}
    )

"""
Dashboard & Reports Service
Handles analytics, reports, and data export
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import io
import csv

from app.models.order import Order, OrderStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
from app.models.product import Product
from app.models.user import User, UserRole


class DashboardService:
    """Dashboard and reports service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_admin_dashboard(self) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Total revenue
        total_revenue = self.db.query(func.sum(Invoice.amount_paid)).filter(
            Invoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
        ).scalar() or 0
        
        # Today's revenue
        from app.models.invoice import PaymentStatus
        today_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= today_start
        ).scalar() or 0
        
        # Week revenue
        week_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= week_start
        ).scalar() or 0
        
        # Month revenue
        month_revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= month_start
        ).scalar() or 0
        
        # Orders count
        total_orders = self.db.query(Order).count()
        active_rentals = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE])
        ).count()
        
        # Pending returns
        pending_returns = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE]),
            Order.rental_end_date <= now + timedelta(days=1)
        ).count()
        
        # Overdue returns
        overdue_returns = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE]),
            Order.rental_end_date < now
        ).count()
        
        # Users count
        total_customers = self.db.query(User).filter(User.role == UserRole.CUSTOMER).count()
        total_vendors = self.db.query(User).filter(User.role == UserRole.VENDOR).count()
        total_products = self.db.query(Product).count()
        
        return {
            "total_revenue": float(total_revenue),
            "total_revenue_today": float(today_revenue),
            "total_revenue_week": float(week_revenue),
            "total_revenue_month": float(month_revenue),
            "total_orders": total_orders,
            "active_rentals": active_rentals,
            "pending_returns": pending_returns,
            "overdue_returns": overdue_returns,
            "total_customers": total_customers,
            "total_vendors": total_vendors,
            "total_products": total_products
        }
    
    def get_vendor_dashboard(self, vendor_id: int) -> Dict[str, Any]:
        """Get vendor dashboard statistics"""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Vendor revenue
        total_revenue = self.db.query(func.sum(Invoice.amount_paid)).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.status.in_([InvoiceStatus.PAID, InvoiceStatus.PARTIALLY_PAID])
        ).scalar() or 0
        
        from app.models.invoice import PaymentStatus
        today_revenue = self.db.query(func.sum(Payment.amount)).join(Invoice).filter(
            Invoice.vendor_id == vendor_id,
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= today_start
        ).scalar() or 0
        
        week_revenue = self.db.query(func.sum(Payment.amount)).join(Invoice).filter(
            Invoice.vendor_id == vendor_id,
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= week_start
        ).scalar() or 0
        
        month_revenue = self.db.query(func.sum(Payment.amount)).join(Invoice).filter(
            Invoice.vendor_id == vendor_id,
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= month_start
        ).scalar() or 0
        
        # Orders
        total_orders = self.db.query(Order).filter(Order.vendor_id == vendor_id).count()
        active_rentals = self.db.query(Order).filter(
            Order.vendor_id == vendor_id,
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE])
        ).count()
        
        pending_pickups = self.db.query(Order).filter(
            Order.vendor_id == vendor_id,
            Order.status.in_([OrderStatus.SALE_ORDER, OrderStatus.CONFIRMED])
        ).count()
        
        pending_returns = self.db.query(Order).filter(
            Order.vendor_id == vendor_id,
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE]),
            Order.rental_end_date <= now + timedelta(days=1)
        ).count()
        
        overdue_returns = self.db.query(Order).filter(
            Order.vendor_id == vendor_id,
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE]),
            Order.rental_end_date < now
        ).count()
        
        total_products = self.db.query(Product).filter(Product.vendor_id == vendor_id).count()
        total_customers = self.db.query(func.count(func.distinct(Order.customer_id))).filter(
            Order.vendor_id == vendor_id
        ).scalar() or 0
        
        return {
            "total_revenue": float(total_revenue),
            "today_revenue": float(today_revenue),
            "week_revenue": float(week_revenue),
            "month_revenue": float(month_revenue),
            "total_orders": total_orders,
            "active_rentals": active_rentals,
            "pending_pickups": pending_pickups,
            "pending_returns": pending_returns,
            "overdue_returns": overdue_returns,
            "total_products": total_products,
            "total_customers": total_customers
        }
    
    def get_revenue_chart(
        self,
        vendor_id: Optional[int] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get revenue chart data for last N days (including today)"""
        now = datetime.utcnow()
        # Ensure we cover the full today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today_start - timedelta(days=days-1)
        
        from app.models.invoice import PaymentStatus
        chart_data = []
        
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            query = self.db.query(func.sum(Payment.amount)).filter(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.payment_date >= day_start,
                Payment.payment_date < day_end
            )
            
            if vendor_id:
                query = query.join(Invoice).filter(Invoice.vendor_id == vendor_id)
            
            revenue = query.scalar() or 0
            
            chart_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "revenue": float(revenue)
            })
        
        return chart_data
    
    def get_top_products(
        self,
        vendor_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most rented products (Confirmed orders only)"""
        from app.models.order import OrderItem, Order, OrderStatus
        
        query = self.db.query(
            Product.id,
            Product.name,
            func.count(OrderItem.id).label("rental_count"),
            func.sum(OrderItem.line_total).label("revenue")
        ).join(OrderItem, Product.id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .filter(Order.status.notin_([OrderStatus.QUOTATION, OrderStatus.CANCELLED]))
        
        if vendor_id:
            query = query.filter(Product.vendor_id == vendor_id)
        
        results = query.group_by(Product.id, Product.name).order_by(
            func.count(OrderItem.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "product_id": r[0],
                "product_name": r[1],
                "rental_count": r[2],
                "revenue": float(r[3] or 0)
            }
            for r in results
        ]
    
    def get_vendor_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get vendor performance data (admin only)"""
        results = self.db.query(
            User.id,
            User.company_name,
            func.count(Order.id).label("total_orders"),
            func.sum(Invoice.amount_paid).label("total_revenue")
        ).join(
            Order, User.id == Order.vendor_id
        ).outerjoin(
            Invoice, Order.id == Invoice.order_id
        ).filter(
            User.role == UserRole.VENDOR
        ).group_by(
            User.id, User.company_name
        ).order_by(
            func.sum(Invoice.amount_paid).desc()
        ).limit(limit).all()
        
        return [
            {
                "vendor_id": r[0],
                "vendor_name": r[1] or "Unknown",
                "total_orders": r[2],
                "total_revenue": float(r[3] or 0)
            }
            for r in results
        ]
    
    def export_orders_csv(
        self,
        vendor_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export orders to CSV"""
        query = self.db.query(Order)
        
        if vendor_id:
            query = query.filter(Order.vendor_id == vendor_id)
        
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        
        orders = query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Order Number", "Customer ID", "Vendor ID", "Status",
            "Rental Start", "Rental End", "Subtotal", "Tax",
            "Total", "Order Date", "Created At"
        ])
        
        # Data
        for order in orders:
            writer.writerow([
                order.order_number,
                order.customer_id,
                order.vendor_id,
                order.status.value,
                order.rental_start_date.isoformat(),
                order.rental_end_date.isoformat(),
                order.subtotal,
                order.tax_amount,
                order.total_amount,
                order.order_date.isoformat(),
                order.created_at.isoformat()
            ])
        
        return output.getvalue()
    
    def export_invoices_csv(
        self,
        vendor_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export invoices to CSV"""
        query = self.db.query(Invoice)
        
        if vendor_id:
            query = query.filter(Invoice.vendor_id == vendor_id)
        
        if start_date:
            query = query.filter(Invoice.invoice_date >= start_date)
        
        if end_date:
            query = query.filter(Invoice.invoice_date <= end_date)
        
        invoices = query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Invoice Number", "Order ID", "Customer", "Vendor",
            "Status", "Subtotal", "Tax", "Total",
            "Amount Paid", "Amount Due", "Invoice Date", "Due Date"
        ])
        
        # Data
        for inv in invoices:
            writer.writerow([
                inv.invoice_number,
                inv.order_id,
                inv.customer_name,
                inv.vendor_company_name,
                inv.status.value,
                inv.subtotal,
                inv.tax_amount,
                inv.total_amount,
                inv.amount_paid,
                inv.amount_due,
                inv.invoice_date.isoformat(),
                inv.due_date.isoformat() if inv.due_date else ""
            ])
        
        return output.getvalue()

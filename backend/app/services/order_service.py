"""
Order Service
Handles quotations, orders, reservations, pickup and return
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.order import Order, OrderItem, OrderStatus, DeliveryMethod
from app.models.product import Product
from app.models.user import User
from app.models.reservation import Reservation, PickupDocument, ReturnDocument, ReservationStatus, StockStatus
from app.schemas.order import OrderCreate, OrderItemCreate, OrderConfirm
from app.services.product_service import ProductService


class OrderService:
    """Order management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.product_service = ProductService(db)
    
    def generate_order_number(self) -> str:
        """Generate unique order number"""
        last_order = self.db.query(Order).order_by(Order.id.desc()).first()
        next_id = (last_order.id + 1) if last_order else 1
        return f"S{datetime.now().strftime('%Y%m')}{next_id:05d}"
    
    def create_quotation(self, customer_id: int, data: OrderCreate) -> Order:
        """Create a new quotation (cart)"""
        # Group items by vendor
        vendor_orders = {}
        
        for item in data.items:
            product = self.product_service.get_product(item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")
            
            # Check availability
            availability = self.product_service.check_availability(
                item.product_id,
                item.rental_start_date,
                item.rental_end_date,
                item.quantity,
                item.variant_id
            )
            
            if not availability["is_available"]:
                raise ValueError(f"Product {product.name} is not available for the selected dates")
            
            vendor_id = product.vendor_id
            if vendor_id not in vendor_orders:
                vendor_orders[vendor_id] = []
            vendor_orders[vendor_id].append((item, product))
        
        created_orders = []
        
        # Create separate order for each vendor
        for vendor_id, items in vendor_orders.items():
            order = Order(
                order_number=self.generate_order_number(),
                customer_id=customer_id,
                vendor_id=vendor_id,
                status=OrderStatus.QUOTATION,
                rental_start_date=data.rental_start_date,
                rental_end_date=data.rental_end_date,
                delivery_method=DeliveryMethod(data.delivery_method.value),
                billing_address=data.billing_address,
                delivery_address=data.delivery_address,
                customer_notes=data.customer_notes,
                discount_code=data.discount_code
            )
            
            self.db.add(order)
            self.db.flush()
            
            # Add items
            for item_data, product in items:
                # Get price based on rental period type
                unit_price = self._get_rental_price(product, item_data.rental_period_type)
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    variant_id=item_data.variant_id,
                    product_name=product.name,
                    product_sku=product.sku,
                    rental_start_date=item_data.rental_start_date,
                    rental_end_date=item_data.rental_end_date,
                    quantity=item_data.quantity,
                    unit_price=unit_price,
                    rental_period_type=item_data.rental_period_type
                )
                order_item.calculate_total(order.tax_rate)
                
                order.security_deposit += product.security_deposit * item_data.quantity
                
                self.db.add(order_item)
            
            order.calculate_totals()
            created_orders.append(order)
        
        self.db.commit()
        
        # Return first order (or could return all)
        return created_orders[0] if created_orders else None
    
    def _get_rental_price(self, product: Product, period_type: str) -> float:
        """Get rental price based on period type"""
        prices = {
            "hourly": product.rental_price_hourly,
            "daily": product.rental_price_daily,
            "weekly": product.rental_price_weekly,
            "monthly": product.rental_price_monthly
        }
        return prices.get(period_type, product.rental_price_daily)
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        return self.db.query(Order).filter(Order.order_number == order_number).first()
    
    def get_orders(
        self,
        customer_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get orders with filters"""
        query = self.db.query(Order)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        if vendor_id:
            query = query.filter(Order.vendor_id == vendor_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "items": orders,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    
    def get_customer_cart(self, customer_id: int) -> Optional[Order]:
        """Get customer's active cart (quotation)"""
        return self.db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.status == OrderStatus.QUOTATION
        ).first()
    
    def add_to_cart(self, customer_id: int, item: OrderItemCreate) -> Order:
        """Add item to cart (create or update quotation)"""
        cart = self.get_customer_cart(customer_id)
        
        product = self.product_service.get_product(item.product_id)
        if not product:
            raise ValueError("Product not found")
        
        # Check availability
        availability = self.product_service.check_availability(
            item.product_id,
            item.rental_start_date,
            item.rental_end_date,
            item.quantity,
            item.variant_id
        )
        
        if not availability["is_available"]:
            raise ValueError(f"Product {product.name} is not available")
        
        if not cart:
            # Create new cart
            cart = Order(
                order_number=self.generate_order_number(),
                customer_id=customer_id,
                vendor_id=product.vendor_id,
                status=OrderStatus.QUOTATION,
                rental_start_date=item.rental_start_date,
                rental_end_date=item.rental_end_date
            )
            self.db.add(cart)
            self.db.flush()
        
        # Check if item already exists
        existing_item = self.db.query(OrderItem).filter(
            OrderItem.order_id == cart.id,
            OrderItem.product_id == item.product_id,
            OrderItem.variant_id == item.variant_id
        ).first()
        
        unit_price = self._get_rental_price(product, item.rental_period_type)
        
        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.calculate_total(cart.tax_rate)
        else:
            order_item = OrderItem(
                product_id=product.id,
                variant_id=item.variant_id,
                product_name=product.name,
                product_sku=product.sku,
                rental_start_date=item.rental_start_date,
                rental_end_date=item.rental_end_date,
                quantity=item.quantity,
                unit_price=unit_price,
                rental_period_type=item.rental_period_type
            )
            order_item.calculate_total(cart.tax_rate)
            cart.items.append(order_item)
            cart.security_deposit += product.security_deposit * item.quantity
        
        self.db.flush()
        cart.calculate_totals()
        self.db.commit()
        self.db.refresh(cart)
        
        return cart
    
    def remove_from_cart(self, customer_id: int, item_id: int) -> Optional[Order]:
        """Remove item from cart"""
        cart = self.get_customer_cart(customer_id)
        
        if not cart:
            return None
        
        item = self.db.query(OrderItem).filter(
            OrderItem.id == item_id,
            OrderItem.order_id == cart.id
        ).first()
        
        if item:
            self.db.delete(item)
            cart.calculate_totals()
            self.db.commit()
            self.db.refresh(cart)
        
        return cart
    
    def confirm_order(self, order_id: int, data: OrderConfirm) -> Order:
        """
        Confirm quotation and convert to sale order
        Creates reservations to prevent double-booking
        """
        order = self.get_order(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status != OrderStatus.QUOTATION:
            if order.status == OrderStatus.SALE_ORDER:
                return order
            raise ValueError("Only quotations can be confirmed")
        
        # Verify availability for all items
        for item in order.items:
            availability = self.product_service.check_availability(
                item.product_id,
                item.rental_start_date,
                item.rental_end_date,
                item.quantity,
                item.variant_id
            )
            
            if not availability["is_available"]:
                raise ValueError(f"Product {item.product_name} is no longer available")
        
        # Update order
        order.status = OrderStatus.SALE_ORDER
        order.delivery_method = data.delivery_method
        order.billing_address = data.billing_address
        order.delivery_address = data.delivery_address
        order.downpayment_amount = data.downpayment_amount or 0
        order.confirmed_at = datetime.utcnow()
        
        # Create reservations for each item
        for item in order.items:
            reservation = Reservation(
                product_id=item.product_id,
                variant_id=item.variant_id,
                order_id=order.id,
                quantity=item.quantity,
                start_date=item.rental_start_date,
                end_date=item.rental_end_date,
                status=ReservationStatus.ACTIVE,
                stock_status=StockStatus.RESERVED
            )
            self.db.add(reservation)
            
            # Update product reserved quantity
            product = self.product_service.get_product(item.product_id)
            product.quantity_reserved += item.quantity
        
        # Create pickup document
        pickup_doc = PickupDocument(
            document_number=f"PU-{order.order_number}",
            order_id=order.id,
            pickup_instructions="Please bring a valid ID for verification",
            pickup_location=order.delivery_address
        )
        self.db.add(pickup_doc)
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def mark_picked_up(self, order_id: int, picked_up_by: str = None, notes: str = None) -> Order:
        """Mark order as picked up"""
        order = self.get_order(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status not in [OrderStatus.SALE_ORDER, OrderStatus.CONFIRMED]:
            raise ValueError("Order must be confirmed before pickup")
        
        order.status = OrderStatus.PICKED_UP
        order.pickup_date = datetime.utcnow()
        order.pickup_notes = notes
        
        # Update reservations
        for reservation in order.reservations:
            reservation.stock_status = StockStatus.WITH_CUSTOMER
        
        # Update pickup document
        pickup_doc = self.db.query(PickupDocument).filter(
            PickupDocument.order_id == order_id
        ).first()
        
        if pickup_doc:
            pickup_doc.is_picked_up = True
            pickup_doc.picked_up_at = datetime.utcnow()
            pickup_doc.picked_up_by = picked_up_by
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def mark_returned(
        self,
        order_id: int,
        received_by: str = None,
        condition_notes: str = None,
        damage_reported: bool = False,
        damage_description: str = None
    ) -> Order:
        """Mark order as returned"""
        order = self.get_order(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status not in [OrderStatus.PICKED_UP, OrderStatus.ACTIVE, OrderStatus.LATE]:
            raise ValueError("Order must be picked up before return")
        
        now = datetime.utcnow()
        
        # Calculate late fees if applicable
        if now > order.rental_end_date:
            days_late = (now - order.rental_end_date).days
            late_fee_per_day = order.total_amount * 0.05  # 5% per day
            order.late_fees_applied = days_late * late_fee_per_day
        
        order.status = OrderStatus.RETURNED
        order.return_date = now
        order.actual_return_date = now
        order.return_notes = condition_notes
        
        # Release reservations
        for reservation in order.reservations:
            reservation.status = ReservationStatus.FULFILLED
            reservation.stock_status = StockStatus.RETURNED
            reservation.released_at = now
            
            # Update product quantity
            product = self.product_service.get_product(reservation.product_id)
            product.quantity_reserved -= reservation.quantity
        
        # Create return document
        return_doc = ReturnDocument(
            document_number=f"RT-{order.order_number}",
            order_id=order.id,
            is_returned=True,
            returned_at=now,
            received_by=received_by,
            condition_notes=condition_notes,
            damage_reported=damage_reported,
            damage_description=damage_description,
            expected_return_date=order.rental_end_date,
            actual_return_date=now,
            is_late=now > order.rental_end_date,
            late_days=(now - order.rental_end_date).days if now > order.rental_end_date else 0,
            late_fee_applied=order.late_fees_applied
        )
        self.db.add(return_doc)
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def cancel_order(self, order_id: int, notes: str = None) -> Order:
        """Cancel order and release reservations"""
        order = self.get_order(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise ValueError("Cannot cancel completed or already cancelled order")
        
        order.status = OrderStatus.CANCELLED
        order.internal_notes = notes
        
        # Release reservations
        for reservation in order.reservations:
            reservation.status = ReservationStatus.RELEASED
            reservation.released_at = datetime.utcnow()
            
            # Update product quantity
            product = self.product_service.get_product(reservation.product_id)
            product.quantity_reserved -= reservation.quantity
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def get_pending_pickups(self, vendor_id: Optional[int] = None) -> List[Order]:
        """Get orders pending pickup"""
        query = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.SALE_ORDER, OrderStatus.CONFIRMED])
        )
        
        if vendor_id:
            query = query.filter(Order.vendor_id == vendor_id)
        
        return query.all()
    
    def get_upcoming_returns(self, vendor_id: Optional[int] = None, days: int = 1) -> List[Order]:
        """Get orders with upcoming returns (within specified days)"""
        from datetime import timedelta
        
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)
        
        query = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE]),
            Order.rental_end_date <= future_date,
            Order.rental_end_date >= now
        )
        
        if vendor_id:
            query = query.filter(Order.vendor_id == vendor_id)
        
        return query.all()
    
    def get_overdue_orders(self, vendor_id: Optional[int] = None) -> List[Order]:
        """Get overdue orders"""
        now = datetime.utcnow()
        
        query = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PICKED_UP, OrderStatus.ACTIVE]),
            Order.rental_end_date < now
        )
        
        if vendor_id:
            query = query.filter(Order.vendor_id == vendor_id)
        
        return query.all()

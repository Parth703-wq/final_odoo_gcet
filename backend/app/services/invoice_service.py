"""
Invoice Service
Handles invoice creation, payments, and Razorpay integration
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import razorpay
import hmac
import hashlib

from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.core.config import settings


class InvoiceService:
    """Invoice management service"""
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize Razorpay client
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            self.razorpay_client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
        else:
            self.razorpay_client = None
    
    def generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        year = datetime.now().year
        last_invoice = self.db.query(Invoice).filter(
            Invoice.invoice_number.like(f"INV/{year}/%")
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split("/")[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        return f"INV/{year}/{next_num:05d}"
    
    def generate_payment_number(self) -> str:
        """Generate unique payment number"""
        last_payment = self.db.query(Payment).order_by(Payment.id.desc()).first()
        next_id = (last_payment.id + 1) if last_payment else 1
        return f"PAY{datetime.now().strftime('%Y%m')}{next_id:05d}"
    
    def create_invoice_from_order(self, order_id: int, due_days: int = 7, notes: str = None) -> Invoice:
        """Create invoice from confirmed order"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise ValueError("Order not found")
        
        # Check if invoice already exists
        invoice = self.db.query(Invoice).filter(Invoice.order_id == order_id).first()
        
        if invoice:
            if invoice.status != InvoiceStatus.DRAFT:
                return invoice
            # If draft, update it to match latest order data
            # Properly clear previous items to sync session
            invoice.items = [] # This is better for sync than query.delete
            # Reset values that will be recalculated
            invoice.subtotal = 0
            invoice.tax_amount = 0
            invoice.total_amount = 0
            invoice.rental_start_date = order.rental_start_date
            invoice.rental_end_date = order.rental_end_date
            invoice.security_deposit = order.security_deposit
            invoice.delivery_charges = order.delivery_charges
            invoice.late_fees = order.late_fees_applied
        else:
            # Get customer and vendor
            customer = self.db.query(User).filter(User.id == order.customer_id).first()
            vendor = self.db.query(User).filter(User.id == order.vendor_id).first()
            
            invoice = Invoice(
                invoice_number=self.generate_invoice_number(),
                order_id=order.id,
                customer_id=order.customer_id,
                vendor_id=order.vendor_id,
                status=InvoiceStatus.DRAFT,
                invoice_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=due_days),
                rental_start_date=order.rental_start_date,
                rental_end_date=order.rental_end_date,
                billing_address=order.billing_address,
                delivery_address=order.delivery_address,
                vendor_company_name=vendor.company_name if vendor else None,
                vendor_gstin=vendor.gstin if vendor else None,
                vendor_logo=vendor.company_logo if vendor else None,
                customer_name=customer.full_name if customer else None,
                customer_gstin=customer.gstin if customer else None,
                tax_rate=order.tax_rate,
                discount_amount=order.discount_amount,
                discount_code=order.discount_code,
                security_deposit=order.security_deposit,
                delivery_charges=order.delivery_charges,
                late_fees=order.late_fees_applied,
                notes=notes
            )
            self.db.add(invoice)
        
        self.db.flush()
        
        # Create invoice items from order items
        for order_item in order.items:
            invoice_item = InvoiceItem(
                invoice=invoice,
                product_name=order_item.product_name,
                product_sku=order_item.product_sku,
                description=f"Rental: {order_item.rental_start_date.strftime('%Y-%m-%d')} to {order_item.rental_end_date.strftime('%Y-%m-%d')}",
                rental_start_date=order_item.rental_start_date,
                rental_end_date=order_item.rental_end_date,
                quantity=order_item.quantity,
                unit="Units",
                unit_price=order_item.unit_price,
                tax_rate=order.tax_rate
            )
            invoice_item.tax_amount = invoice_item.quantity * invoice_item.unit_price * (invoice_item.tax_rate / 100)
            # Default to split GST
            invoice_item.cgst = invoice_item.tax_amount / 2
            invoice_item.sgst = invoice_item.tax_amount / 2
            invoice_item.igst = 0.0
            
            invoice_item.line_total = (invoice_item.quantity * invoice_item.unit_price) + invoice_item.tax_amount
            # No need to append explicitly if invoice=invoice is set, BUT it helps some sync issues
            if invoice_item not in invoice.items:
                invoice.items.append(invoice_item)
        
        # Add security deposit as line item if applicable
        if order.security_deposit > 0:
            deposit_item = InvoiceItem(
                invoice=invoice,
                product_name="Security Deposit",
                description="Refundable security deposit",
                quantity=1,
                unit="Units",
                unit_price=order.security_deposit,
                tax_rate=0,
                tax_amount=0,
                line_total=order.security_deposit
            )
            if deposit_item not in invoice.items:
                invoice.items.append(deposit_item)
        
        self.db.flush()
        # Ensure items are matched in the object
        invoice.calculate_totals()
        
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID with items joined"""
        from sqlalchemy.orm import joinedload
        return self.db.query(Invoice).options(joinedload(Invoice.items)).filter(Invoice.id == invoice_id).first()
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by number"""
        return self.db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    
    def get_invoices(
        self,
        customer_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get invoices with filters"""
        query = self.db.query(Invoice)
        
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        
        if vendor_id:
            query = query.filter(Invoice.vendor_id == vendor_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if start_date:
            query = query.filter(Invoice.invoice_date >= start_date)
        
        if end_date:
            query = query.filter(Invoice.invoice_date <= end_date)
        
        total = query.count()
        invoices = query.order_by(Invoice.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "items": invoices,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    
    def post_invoice(self, invoice_id: int) -> Invoice:
        """Post invoice (make it official)"""
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            raise ValueError("Invoice not found")
        
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Only draft invoices can be posted")
        
        invoice.status = InvoiceStatus.POSTED
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    # Razorpay Integration
    
    def create_razorpay_order(self, invoice_id: int, amount: Optional[float] = None) -> Dict[str, Any]:
        """Create Razorpay order for payment"""
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            raise ValueError("Invoice not found")
        
        if not self.razorpay_client:
            raise ValueError("Razorpay not configured")
        
        # Use full amount due if not specified
        payment_amount = amount or invoice.amount_due
        
        # Convert to paise (Razorpay requires amount in smallest currency unit)
        amount_in_paise = int(payment_amount * 100)
        
        # Create Razorpay order
        razorpay_order = self.razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"inv_{invoice.invoice_number}",
            "notes": {
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number
            }
        })
        
        return {
            "razorpay_order_id": razorpay_order["id"],
            "amount": amount_in_paise,
            "currency": "INR",
            "invoice_id": invoice.id,
            "key_id": settings.RAZORPAY_KEY_ID
        }
    
    def verify_razorpay_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        invoice_id: int
    ) -> Payment:
        """Verify and record Razorpay payment"""
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            raise ValueError("Invoice not found")
        
        # Verify signature
        if self.razorpay_client:
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if generated_signature != razorpay_signature:
                raise ValueError("Invalid payment signature")
            
            # Get payment details from Razorpay
            payment_details = self.razorpay_client.payment.fetch(razorpay_payment_id)
            amount = payment_details["amount"] / 100  # Convert from paise
        else:
            # For testing without Razorpay
            amount = invoice.amount_due
        
        # Create payment record
        payment = Payment(
            payment_number=self.generate_payment_number(),
            invoice_id=invoice.id,
            order_id=invoice.order_id,
            amount=amount,
            payment_method=PaymentMethod.RAZORPAY,
            status=PaymentStatus.COMPLETED,
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            payment_date=datetime.utcnow()
        )
        
        self.db.add(payment)
        
        # Update invoice
        invoice.amount_paid += amount
        invoice.amount_due = invoice.total_amount - invoice.amount_paid
        
        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.PAID
            
            # Update order status
            order = self.db.query(Order).filter(Order.id == invoice.order_id).first()
            if order and order.status == OrderStatus.SALE_ORDER:
                order.status = OrderStatus.CONFIRMED
                order.downpayment_paid = True
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def record_cash_payment(self, invoice_id: int, amount: float, notes: str = None) -> Payment:
        """Record cash payment"""
        invoice = self.get_invoice(invoice_id)
        
        if not invoice:
            raise ValueError("Invoice not found")
        
        payment = Payment(
            payment_number=self.generate_payment_number(),
            invoice_id=invoice.id,
            order_id=invoice.order_id,
            amount=amount,
            payment_method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
            notes=notes,
            payment_date=datetime.utcnow()
        )
        
        self.db.add(payment)
        
        # Update invoice
        invoice.amount_paid += amount
        invoice.amount_due = invoice.total_amount - invoice.amount_paid
        
        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def get_payments(
        self,
        invoice_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get payments with filters"""
        query = self.db.query(Payment)
        
        if invoice_id:
            query = query.filter(Payment.invoice_id == invoice_id)
        
        if status:
            query = query.filter(Payment.status == status)
        
        total = query.count()
        payments = query.order_by(Payment.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "items": payments,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }

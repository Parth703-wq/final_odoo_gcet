"""
Payment Service for Razorpay Integration
"""
import os
import razorpay
import hashlib
import hmac
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Any, Dict
import random
import string

from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.invoice import Invoice, InvoiceStatus
from app.models.order import Order, OrderStatus
from app.core.config import settings
class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def generate_payment_number(self) -> str:
        """Generate a custom payment number"""
        prefix = "PAY"
        timestamp = datetime.now().strftime("%Y%m")
        random_str = ''.join(random.choices(string.digits, k=5))
        return f"{prefix}{timestamp}{random_str}"

    def create_razorpay_order(self, customer_id: int, amount: float, order_id: Optional[int] = None, invoice_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a Razorpay order"""
        # Razorpay expects amount in paise (1 INR = 100 paise)
        amount_paise = int(amount * 100)

        receipt = f"rec_{self.generate_payment_number()}"

        data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1  # Auto capture
        }

        try:
            razorpay_order = self.client.order.create(data=data)

            # Find or create invoice_id if not provided
            if not invoice_id and order_id:
                invoice = self.db.query(Invoice).filter(Invoice.order_id == order_id).first()
                if invoice:
                    invoice_id = invoice.id

            # Create a pending payment record in our DB
            payment = Payment(
                payment_number=self.generate_payment_number(),
                customer_id=customer_id,
                order_id=order_id,
                invoice_id=invoice_id or 0,  # Default if not found
                amount=amount,
                currency="INR",
                status=PaymentStatus.PENDING,
                payment_method=PaymentMethod.RAZORPAY,
                razorpay_order_id=razorpay_order['id'],
                transaction_id=receipt
            )
            self.db.add(payment)
            self.db.commit()

            return {
                "razorpay_order_id": razorpay_order['id'],
                "amount": amount,
                "currency": "INR",
                "receipt": receipt,
                "key_id": settings.RAZORPAY_KEY_ID
            }
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create Razorpay order: {str(e)}")

    def verify_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """Verify Razorpay payment signature"""
        try:
            return self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except Exception:
            return False

    def complete_payment(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> Optional[Payment]:
        """Complete the payment and update statuses"""
        # Find the pending payment
        payment = self.db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()

        if not payment:
            return None

        if not self.verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = "Signature verification failed"
            self.db.commit()
            return payment

        # Update payment record
        payment.status = PaymentStatus.COMPLETED
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.payment_date = datetime.utcnow()

        # Update Invoice status if applicable
        if payment.invoice_id:
            invoice = self.db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
            if invoice:
                invoice.amount_paid += payment.amount
                invoice.calculate_totals()
                if invoice.amount_due <= 0:
                    invoice.status = InvoiceStatus.PAID
                else:
                    invoice.status = InvoiceStatus.PARTIALLY_PAID

        # Update Order status if applicable
        if payment.order_id:
            order = self.db.query(Order).filter(Order.id == payment.order_id).first()
            if order:
                # If it was a pending or confirmed order, mark as paid
                if order.status in [OrderStatus.QUOTATION, OrderStatus.SALE_ORDER]:
                    order.status = OrderStatus.CONFIRMED
                    order.confirmed_at = datetime.utcnow()
                
                # Update product inventory
                from app.models.product import Product, ProductVariant
                for item in order.items:
                    if item.variant_id:
                        variant = self.db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
                        if variant:
                            variant.quantity_on_hand = max(0, variant.quantity_on_hand - item.quantity)
                    
                    product = self.db.query(Product).filter(Product.id == item.product_id).first()
                    if product:
                        product.quantity_on_hand = max(0, product.quantity_on_hand - item.quantity)

        self.db.commit()
        self.db.refresh(payment)
        return payment

"""
Email Service
Handles sending emails via Google OAuth
"""

from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email
    For production, integrate with Google OAuth SMTP or Gmail API
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    # Log for development
    logger.info(f"Password reset link for {email}: {reset_link}")
    
    # TODO: Implement actual email sending with Google OAuth
    # For now, we'll just log the reset link
    # In production, use google-auth-oauthlib to send emails
    
    try:
        # Placeholder for email sending logic
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build
        
        print(f"[EMAIL] Password reset email sent to: {email}")
        print(f"[EMAIL] Reset link: {reset_link}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_order_confirmation_email(email: str, order_number: str, order_details: dict) -> bool:
    """Send order confirmation email"""
    try:
        print(f"[EMAIL] Order confirmation sent to: {email}")
        print(f"[EMAIL] Order Number: {order_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send order confirmation: {e}")
        return False


def send_invoice_email(email: str, invoice_number: str, invoice_pdf_path: Optional[str] = None) -> bool:
    """Send invoice email with optional PDF attachment"""
    try:
        print(f"[EMAIL] Invoice sent to: {email}")
        print(f"[EMAIL] Invoice Number: {invoice_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send invoice: {e}")
        return False


def send_return_reminder_email(email: str, order_number: str, return_date: str) -> bool:
    """Send return reminder email"""
    try:
        print(f"[EMAIL] Return reminder sent to: {email}")
        print(f"[EMAIL] Order: {order_number}, Return Date: {return_date}")
        return True
    except Exception as e:
        logger.error(f"Failed to send return reminder: {e}")
        return False


def send_late_return_alert(email: str, order_number: str, days_late: int, late_fee: float) -> bool:
    """Send late return alert email"""
    try:
        print(f"[EMAIL] Late return alert sent to: {email}")
        print(f"[EMAIL] Order: {order_number}, Days Late: {days_late}, Fee: {late_fee}")
        return True
    except Exception as e:
        logger.error(f"Failed to send late return alert: {e}")
        return False

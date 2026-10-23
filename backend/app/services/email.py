import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.services.email")


def send_email_sync(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> bool:
    """Send an email using SMTP configured via environment variables."""
    # Check if SMTP credentials are fully provided
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(
            "[DEV/NOT-CONFIGURED] Skipping live SMTP send (credentials not in .env). Email to: %s | Subject: '%s'",
            to_email,
            subject,
        )
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email

    if text_content:
        msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Successfully sent email to %s with subject: '%s'", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, str(exc))
        return False


def send_feedback_notification_email(
    name: str,
    email: str,
    phone: Optional[str],
    rating: int,
    message: str,
) -> None:
    """Send automated emails when a customer submits feedback/contact form."""
    admin_subject = f"New Feedback Received ({rating}/5 Stars) - MrShine Car Wash"
    admin_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #111;">New Feedback Submitted</h2>
        <p>A customer has submitted feedback through the MrShine website:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
          <tr><td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;">Name:</td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{name}</td></tr>
          <tr><td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;">Email:</td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{email}</td></tr>
          <tr><td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;">Phone:</td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{phone or 'Not provided'}</td></tr>
          <tr><td style="padding: 8px; font-weight: bold; border-bottom: 1px solid #ddd;">Rating:</td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{'⭐' * rating} ({rating}/5)</td></tr>
        </table>
        <p><strong>Feedback:</strong></p>
        <blockquote style="background: #f8f8f8; padding: 12px; border-left: 4px solid #111; margin: 10px 0;">{message}</blockquote>
      </body>
    </html>
    """

    customer_subject = "Thank you for contacting MrShine Car Wash!"
    customer_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #111;">Thank You, {name}!</h2>
        <p>We received your feedback / message and appreciate you taking the time to write to us.</p>
        <p>Our team reviews all customer inquiries promptly. If your message requires a follow-up, we will contact you at <strong>{email}</strong>.</p>
        <br/>
        <p>Best regards,<br/><strong>MrShine Car Wash & Detailing Team</strong></p>
      </body>
    </html>
    """

    # Send to admin
    target_admin = settings.ADMIN_EMAIL or settings.EMAILS_FROM_EMAIL
    send_email_sync(to_email=target_admin, subject=admin_subject, html_content=admin_html)

    # Send confirmation to customer
    if email:
        send_email_sync(to_email=email, subject=customer_subject, html_content=customer_html)


def send_service_request_email(
    customer_name: str,
    customer_email: str,
    service_name: str,
    vehicle_details: str,
    date_str: str,
    time_str: str,
) -> None:
    """Notify customer and admin upon service request creation."""
    subject = f"Service Request Received: {service_name} - MrShine"
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #111;">Service Request Confirmed</h2>
        <p>Hello {customer_name},</p>
        <p>Your request for <strong>{service_name}</strong> has been received by MrShine Car Wash.</p>
        <ul>
          <li><strong>Vehicle:</strong> {vehicle_details}</li>
          <li><strong>Preferred Date:</strong> {date_str}</li>
          <li><strong>Preferred Time:</strong> {time_str}</li>
          <li><strong>Status:</strong> Pending Approval</li>
        </ul>
        <p>You can track your request status directly in your MrShine account dashboard.</p>
        <br/>
        <p>Thank you for choosing MrShine!</p>
      </body>
    </html>
    """
    send_email_sync(to_email=customer_email, subject=subject, html_content=html)


def send_status_update_email(
    customer_name: str,
    customer_email: str,
    service_name: str,
    status: str,
) -> None:
    """Send notification when admin approves or rejects a request."""
    subject = f"Your MrShine Service Request Has Been {status}"
    color = "#15803d" if status.lower() == "approved" else "#b91c1c"
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: {color};">Request {status}</h2>
        <p>Hello {customer_name},</p>
        <p>Your service request for <strong>{service_name}</strong> has been marked as <strong>{status}</strong> by our team.</p>
        <p>Please visit your MrShine dashboard to view full details.</p>
        <br/>
        <p>Warm regards,<br/><strong>MrShine Car Wash & Detailing</strong></p>
      </body>
    </html>
    """
    send_email_sync(to_email=customer_email, subject=subject, html_content=html)

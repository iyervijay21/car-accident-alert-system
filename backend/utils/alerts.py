from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from ..core.config import settings
from typing import List

def send_sms(to: str, message: str) -> bool:
    """
    Send SMS using Twilio
    """
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
            print("Twilio credentials not configured")
            return False
            
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False

def send_email(to: str, subject: str, content: str) -> bool:
    """
    Send email using SendGrid
    """
    try:
        if not settings.SENDGRID_API_KEY or not settings.EMAIL_FROM:
            print("SendGrid credentials not configured")
            return False
            
        message = Mail(
            from_email=settings.EMAIL_FROM,
            to_emails=to,
            subject=subject,
            html_content=content
        )
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_alerts(to_contacts: List[dict], accident_info: dict) -> List[dict]:
    """
    Send alerts to all emergency contacts
    """
    results = []
    
    for contact in to_contacts:
        # Send SMS if phone number is provided
        if contact.get("phone_number"):
            message = f"EMERGENCY ALERT: Car accident detected at {accident_info.get('location', 'unknown location')}. Confidence: {accident_info.get('confidence', 0)*100:.1f}%"
            success = send_sms(contact["phone_number"], message)
            results.append({
                "contact_id": contact["id"],
                "type": "SMS",
                "recipient": contact["phone_number"],
                "success": success
            })
        
        # Send email if email is provided
        if contact.get("email"):
            subject = "EMERGENCY ALERT: Car Accident Detected"
            content = f"""
            <h2>EMERGENCY ALERT</h2>
            <p>A car accident has been detected at {accident_info.get('location', 'unknown location')}.</p>
            <p>Confidence Level: {accident_info.get('confidence', 0)*100:.1f}%</p>
            <p>Time: {accident_info.get('time', 'unknown time')}</p>
            """
            success = send_email(contact["email"], subject, content)
            results.append({
                "contact_id": contact["id"],
                "type": "EMAIL",
                "recipient": contact["email"],
                "success": success
            })
    
    return results
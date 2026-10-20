import smtplib
from email.message import EmailMessage
import os
import mimetypes
from typing import List, Optional
from app.core.config import settings

def send_email(subject: str, body: str, to_emails: List[str], attachment_path: Optional[str] = None):
    """
    Gửi email thông báo đơn giản (hỗ trợ đính kèm file)
    """
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print("Email configuration is missing. Skip sending email.")
        return
        
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = settings.MAIL_FROM
    msg['To'] = ", ".join(to_emails)

    if attachment_path and os.path.exists(attachment_path):
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        
        with open(attachment_path, 'rb') as f:
            msg.add_attachment(f.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=os.path.basename(attachment_path))

    try:
        server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
        if settings.MAIL_STARTTLS:
            server.starttls()
        if settings.USE_CREDENTIALS:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_emails}")
    except Exception as e:
        print(f"Failed to send email: {e}")

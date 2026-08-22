import logging
from email.message import EmailMessage

from aiosmtplib import SMTP

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    async def send_email(
        to_email: str, subject: str, body: str, is_html: bool = False
    ) -> bool:
        settings = get_settings()

        message = EmailMessage()
        message["From"] = settings.smtp_from_email
        message["To"] = to_email
        message["Subject"] = subject

        if is_html:
            message.add_alternative(body, subtype="html")
        else:
            message.set_content(body)

        try:
            smtp_client = SMTP(
                hostname=settings.smtp_hostname,
                port=settings.smtp_port,
                username=settings.smtp_username or None,
                password=settings.smtp_password or None,
                use_tls=settings.smtp_use_tls,
            )
            async with smtp_client:
                await smtp_client.send_message(message)
            logger.info(f"Successfully sent email to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

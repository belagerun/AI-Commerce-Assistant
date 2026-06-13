import smtplib
from email.message import EmailMessage

from config import settings


SMTP_CONFIG_ERROR = (
    "Email service is not configured. Please set SMTP_HOST, SMTP_PORT, "
    "SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM."
)
SMTP_TIMEOUT_SECONDS = 10


class EmailService:
    def send_verification_email(self, recipient_email: str, code: str) -> None:
        if not self.is_configured():
            raise ValueError(SMTP_CONFIG_ERROR)

        message = EmailMessage()
        message["Subject"] = "Your AI Commerce Assistant verification code"
        message["From"] = settings.SMTP_FROM
        message["To"] = recipient_email
        message.set_content(
            f"Your verification code is: {code}. It will expire in 10 minutes."
        )

        try:
            print(f"SMTP send started for {recipient_email}")
            with smtplib.SMTP(
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                timeout=SMTP_TIMEOUT_SECONDS,
            ) as smtp:
                smtp.starttls()
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
            print(f"SMTP send finished for {recipient_email}")
        except smtplib.SMTPException as error:
            print(f"SMTP send failed for {recipient_email}: {error}")
            raise ValueError(f"Failed to send verification email: {error}") from error
        except (OSError, TimeoutError) as error:
            print(f"SMTP send failed for {recipient_email}: {error}")
            raise ValueError(f"Failed to connect to email service: {error}") from error

    def is_configured(self) -> bool:
        return all(
            (
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
                settings.SMTP_FROM,
            )
        )

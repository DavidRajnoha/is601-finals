# email_service.py
from builtins import ValueError, dict, str
from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

from logging import getLogger
logger = getLogger(__name__)

class EmailService:
    def __init__(self, template_manager: TemplateManager):
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager

    def send_user_email(self, user_data: dict, email_type: str):
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification",
            'account_unlocked': "Account Unlocked Notification",
            'role_upgrade': "Role Upgrade Notification",
            'professional_status_upgrade': "Professional Status Upgrade Notification"
        }

        if email_type not in subject_map:
            raise ValueError("Invalid email type")

        html_content = self.template_manager.render_template(email_type, **user_data)
        self.smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])

    def send_verification_email(self, user: User):
        logger.error(f"Sending verification email to {user.email}")
        verification_url = f"{settings.server_base_url}verify-email/{user.id}/{user.verification_token}"

        return self.send_user_email({
            "name": user.first_name,
            "verification_url": verification_url,
            "email": user.email
        }, 'email_verification')

    def send_account_locked_email(self, user: User):
        logger.error(f"Sending account locked email to {user.email}")
        return self.send_user_email({
            "name": user.first_name,
            "email": user.email
        }, 'account_locked')

    def send_account_unlocked_email(self, user: User):
        logger.error(f"Sending account unlocked email to {user.email}")
        return self.send_user_email({
            "name": user.first_name,
            "email": user.email
        }, 'account_unlocked')

    def send_role_upgrade_email(self, user: User, new_role: str):
        logger.error(f"Sending role upgrade email to {user.email}")
        return self.send_user_email({
            "name": user.first_name,
            "new_role": new_role,
            "email": user.email
        }, 'role_upgrade')

    def send_professional_status_upgrade_email(self, user: User):
        logger.error(f"Sending professional status upgrade email to {user.email}")
        return self.send_user_email({
            "name": user.first_name,
            "email": user.email
        }, 'professional_status_upgrade')

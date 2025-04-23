from app.celery.celery_app import celery
from app.dependencies import get_email_service
from app.models.user_model import User

email_service = get_email_service()

# import logging

# logger = logging.getLogger(__name__)

@celery.task(name="account.verification", queue="default")
def verification_task(*args, **kwargs):
    # logger.info("Verification task started")
    return True

@celery.task(name="account.send_verification", queue="emails")
def verify_task(user: User):
    email_service.send_verification_email(user)



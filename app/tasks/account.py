from app.celery_app import celery

# import logging

# logger = logging.getLogger(__name__)

@celery.task(name="account.verification")
def verification_task(*args, **kwargs):
    # logger.info("Verification task started")
    return True
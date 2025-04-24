from app.celery.celery_app import celery
from app.dependencies import get_email_service, get_sync_db
from app.models.user_model import User

@celery.task(name="account.verification", queue="default")
def verification_task(*args, **kwargs):
    return True

@celery.task(name="account.send_verification", queue="emails")
def verify_email_task(
    user_id: int,
    email_svc=None,
    session_factory=None
):
    """
    Send a verification email for the given user_id.

    Dependencies can be overridden for testing:
      • email_svc       – an object with send_user_email(user)
      • session_factory – a callable returning a DB session supporting .get()
    """
    email_svc = email_svc or get_email_service()
    session_factory = session_factory or get_sync_db

    with session_factory() as session:
        user = session.get(User, user_id)
        email_svc.send_verification_email(user)
    return True

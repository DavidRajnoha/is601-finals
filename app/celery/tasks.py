from app.celery.celery_app import celery
from app.dependencies import get_email_service, get_sync_db
from app.models.user_model import User

@celery.task(name="account.verification", queue="default")
def verification_task(*args, **kwargs):
    return True

@celery.task(name="account.send_verification", queue="account_notifications")
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

@celery.task(name="account.locked", queue="account_notifications")
def account_locked_task(
    user_id: int,
    email_svc=None,
    session_factory=None
):
    """
    Send an account locked notification email for the given user_id.

    Dependencies can be overridden for testing:
      • email_svc       – an object with send_account_locked_email(user)
      • session_factory – a callable returning a DB session supporting .get()
    """
    email_svc = email_svc or get_email_service()
    session_factory = session_factory or get_sync_db

    with session_factory() as session:
        user = session.get(User, user_id)
        email_svc.send_account_locked_email(user)
    return True

@celery.task(name="account.unlocked", queue="account_notifications")
def account_unlocked_task(
    user_id: int,
    email_svc=None,
    session_factory=None
):
    """
    Send an account unlocked notification email for the given user_id.

    Dependencies can be overridden for testing:
      • email_svc       – an object with send_account_unlocked_email(user)
      • session_factory – a callable returning a DB session supporting .get()
    """
    email_svc = email_svc or get_email_service()
    session_factory = session_factory or get_sync_db

    with session_factory() as session:
        user = session.get(User, user_id)
        email_svc.send_account_unlocked_email(user)
    return True

@celery.task(name="account.role_upgrade", queue="account_notifications")
def role_upgrade_task(
    user_id: int,
    new_role: str,
    email_svc=None,
    session_factory=None
):
    """
    Send a role upgrade notification email for the given user_id.

    Dependencies can be overridden for testing:
      • email_svc       – an object with send_role_upgrade_email(user, new_role)
      • session_factory – a callable returning a DB session supporting .get()
    """
    email_svc = email_svc or get_email_service()
    session_factory = session_factory or get_sync_db

    with session_factory() as session:
        user = session.get(User, user_id)
        email_svc.send_role_upgrade_email(user, new_role)
    return True

@celery.task(name="account.professional_status_upgrade", queue="account_notifications")
def professional_status_upgrade_task(
    user_id: int,
    email_svc=None,
    session_factory=None
):
    """
    Send a professional status upgrade notification email for the given user_id.

    Dependencies can be overridden for testing:
      • email_svc       – an object with send_professional_status_upgrade_email(user)
      • session_factory – a callable returning a DB session supporting .get()
    """
    email_svc = email_svc or get_email_service()
    session_factory = session_factory or get_sync_db

    with session_factory() as session:
        user = session.get(User, user_id)
        email_svc.send_professional_status_upgrade_email(user)
    return True

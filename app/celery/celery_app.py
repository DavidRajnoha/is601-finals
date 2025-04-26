from celery import Celery
from kombu import Exchange, Queue

from app.database import Database
from app.dependencies import get_settings

settings = get_settings()

Database.initialize(
    database_url     = None,
    sync_database_url= settings.sync_database_url,
    echo             = settings.debug
)

celery = Celery(
    "myapp",
    broker=settings.broker_url,
    backend="rpc://"
)

celery.autodiscover_tasks(["app.celery"])

celery.conf.update(
    task_default_queue="default",
    task_default_exchange="default",
    task_default_exchange_type="direct",
    task_queues=[
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("account_notifications", Exchange("account_notifications"), routing_key="account.notifications"),
    ],
    task_routes={
        "account.send_verification": {"queue": "account_notifications", "routing_key": "account.notifications"},
        "account.locked": {"queue": "account_notifications", "routing_key": "account.notifications"},
        "account.unlocked": {"queue": "account_notifications", "routing_key": "account.notifications"},
        "account.role_upgrade": {"queue": "account_notifications", "routing_key": "account.notifications"},
        "account.professional_status_upgrade": {"queue": "account_notifications", "routing_key": "account.notifications"},
        "reports.generate": {"queue": "reports", "routing_key": "reports.generate"},
    },
)

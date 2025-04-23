from celery import Celery
from kombu import Exchange, Queue

from app.dependencies import get_settings

settings = get_settings()

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
        Queue("emails", Exchange("emails"), routing_key="account.send_verification"),
    ],
    task_routes={
        "account.send_verification": {"queue": "emails", "routing_key": "account.send_verification"},
        "reports.generate": {"queue": "reports", "routing_key": "reports.generate"},
    },
)
from celery import Celery

from app.dependencies import get_settings

settings = get_settings()

celery = Celery(
    "myapp",
    broker=settings.broker_url,
    backend="rpc://"
)
celery.autodiscover_tasks(["app.tasks"])

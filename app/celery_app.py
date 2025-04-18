from celery import Celery
from settings.config import settings

celery = Celery(
    "myapp",
    broker=settings.broker_url,
)
celery.autodiscover_tasks(["app.tasks"])

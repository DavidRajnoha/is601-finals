import pytest
from kombu.exceptions import OperationalError

from app.dependencies import get_settings

settings = get_settings()

@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": settings.broker_url,
        "result_backend": "rpc://",
    }


@pytest.mark.rabbitmq
def test_broker(ping_broker, celery_app, celery_worker):
    """
    Smoke-test the production Celery stack.

    Verifies the connection to the broker as defined in conftest.py.
    """
    @celery_app.task
    def mul(x, y):
        return x * y

    celery_worker.reload()
    assert mul.delay(4, 4).get(timeout=10) == 16

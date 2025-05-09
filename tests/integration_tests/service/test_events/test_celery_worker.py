import pytest
from kombu.exceptions import OperationalError

from app.celery.celery_app import celery as real_app

@pytest.fixture(scope="session")
def celery_app():
    return real_app


@pytest.fixture(scope="session")
def use_celery_app_trap():
    return True

@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"shutdown_timeout": 30}

@pytest.mark.rabbitmq
def test_broker_real_app(ping_broker, celery_app):
    """
    • Confirms the external worker is alive (via ping).
    • Sends the real `verification_task` into RabbitMQ.
    • Blocks on .get() until the Docker worker processes it.
    """

    async_res = celery_app.send_task(
        "account.verification",
        args=("foo@example.com",),
        queue="default"
    )

    assert async_res.get(timeout=20) is True

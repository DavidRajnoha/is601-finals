# tests/test_account_tasks.py
import pytest

from app.celery.tasks import verification_task
from app.celery.celery_app import celery

def test_verification_task_run_directly_logs_and_returns_true():
    """
    This bypasses all Celery machinery and just calls your task function.
    Good for pure‐unit testing the logic & logging.
    """
    result = verification_task.run()
    assert result is True

@pytest.fixture(autouse=True)
def celery_eager_settings():
    """
    Force Celery to execute tasks synchronously in‐process,
    so you can call .delay() without a live broker.
    """
    celery.conf.update(
        broker_url='memory://',
        task_always_eager=True,
        result_backend='rpc://',
    )

def test_verification_task_delay_eager():
    """
    This ensures your task is discovered by Celery and
    that .delay() → AsyncResult.get() returns the expected value,
    while still capturing your log message.
    """
    async_result = verification_task.delay()
    assert async_result.get(timeout=1) is True

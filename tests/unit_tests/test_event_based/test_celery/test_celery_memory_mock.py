from app.tasks.account import verification_task
import pytest
from app.celery_app import celery as real_app


@real_app.task(name="celery.ping")
def _ping():
    return "pong"

@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url":     "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": False,
    }

@pytest.fixture(scope="session")
def celery_app():
    real_app.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
    )
    return real_app


@pytest.fixture(scope="session")
def celery_worker_pool():
    return "solo"

# tests/test_account_tasks.py
def test_through_memory_broker(celery_app, celery_worker, mocker):
    async_result = verification_task.delay("foo@example.com")
    assert async_result.get(timeout=5) is True

import pytest
from app.celery.tasks import verification_task
from app.celery.celery_app import celery as real_app


@pytest.fixture(scope="session")
def celery_app():
    return real_app

@pytest.fixture(scope="session")
def use_celery_app_trap():
    return True

@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"without_heartbeat": False,
            "shutdown_timeout": 30,
            "perform_ping_check": False,
            }

@pytest.mark.rabbitmq
def test_broker_real_app(celery_app, celery_worker):
    """
    Smoke-test the production Celery stack.

    • Uses the real `celery` app → verifies its broker & backend URLs.
    • `verification_task.delay()` must reach the broker, run in the
      worker, and return a truthy result within 10 s.
    • `use_celery_app_trap` ensures no code falls back to
      `current_app`.
    • `celery_worker.reload()` confirms tasks stay discoverable after a
      worker restart.

    Any timeout or exception flags a broken broker, backend, or task
    registration.
    """
    celery_worker.reload()
    result = verification_task.delay("foo@example.com").get(timeout=10)

    assert result

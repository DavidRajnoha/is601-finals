import pytest
from kombu.exceptions import OperationalError


def pytest_configure(config):
    config.pluginmanager.set_blocked("pytest_celery")   # disable locally
    config.pluginmanager.import_plugin("celery.contrib.pytest")


@pytest.fixture(scope="session")
def celery_parameters():
    return {
        "task_always_eager": False,
        "task_store_eager_result": False,
    }

@pytest.fixture(scope="function")
def ping_broker(celery_app):
    try:
        res = celery_app.control.ping(timeout=5)
    except OperationalError as e:
        pytest.skip(f"Cannot connect to rabbitmq: {e}")
    assert res, "No response from any worker"
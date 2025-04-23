import pytest


def pytest_configure(config):
    config.pluginmanager.set_blocked("pytest_celery")   # disable locally
    config.pluginmanager.import_plugin("celery.contrib.pytest")


@pytest.fixture(scope="session")
def celery_parameters():
    return {
        "task_always_eager": False,
        "task_store_eager_result": False,
    }
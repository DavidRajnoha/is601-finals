"""
tests/test_database.py

Behaviour-level tests for the `Database` singleton:

* Correct initialisation of async and sync engines.
* Re-use of singleton instances on repeated calls.
* Proper raising of `RuntimeError` when factories are requested
  before the corresponding side is initialised.
* Isolation of global state between tests.
"""

import inspect
import pytest
from sqlalchemy import text
from app.database import Database


def _reset_singletons() -> None:
    """Hard-reset all class-level singleton attributes."""
    for attr in (
        "_async_engine",
        "_async_session_factory",
        "_sync_engine",
        "_sync_session_factory",
    ):
        setattr(Database, attr, None)


@pytest.fixture(autouse=True)
def isolate_database_singletons():
    """Ensure every test starts with a clean `Database` singleton."""
    _reset_singletons()
    yield
    _reset_singletons()


@pytest.mark.asyncio
async def test_async_initialisation_and_singleton_reuse() -> None:
    """Initialising twice with the same URL must return the same async objects."""
    url_async = "sqlite+aiosqlite:///:memory:"

    Database.initialize(url_async, None, echo=True)
    factory_1 = Database.get_async_factory()
    engine_1 = Database._async_engine

    Database.initialize(url_async, None)  # second call: no new objects
    assert Database._async_engine is engine_1
    assert Database.get_async_factory() is factory_1

    async with factory_1() as session:
        assert (await session.execute(text("SELECT 1"))).scalar() == 1


def test_sync_initialisation_and_singleton_reuse() -> None:
    """Sync side mirrors the async behaviour: single initialisation, singletons re-used."""
    url_sync = "sqlite:///:memory:"

    Database.initialize(None, url_sync)
    factory_1 = Database.get_sync_factory()
    engine_1 = Database._sync_engine

    Database.initialize(None, url_sync)
    assert Database._sync_engine is engine_1
    assert Database.get_sync_factory() is factory_1

    with factory_1() as session:
        assert session.execute(text("SELECT 1")).scalar() == 1


def test_get_async_factory_without_init_raises() -> None:
    """Calling `get_async_factory` before initialisation should explode immediately."""
    with pytest.raises(RuntimeError):
        Database.get_async_factory()


def test_get_sync_factory_without_init_raises() -> None:
    """Calling `get_sync_factory` before initialisation should explode immediately."""
    with pytest.raises(RuntimeError):
        Database.get_sync_factory()


def test_partial_initialisation_is_respected() -> None:
    """
    If only one side is initialised, the other side must still raise
    `RuntimeError` when its factory is requested.
    """
    Database.initialize("sqlite+aiosqlite:///:memory:", None)
    assert inspect.isclass(Database.get_async_factory().__class__)

    with pytest.raises(RuntimeError):
        Database.get_sync_factory()

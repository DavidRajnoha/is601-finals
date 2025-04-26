# tests/test_database_async.py

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Database

ASYNC_URL = "sqlite+aiosqlite:///:memory:"


def setup_module(module):
    """Reset async engine and factory before tests."""
    Database._async_engine = None
    Database._async_session_factory = None


@pytest.mark.asyncio
async def test_async_factory_uninitialized_raises():
    """get_async_factory() should raise if initialize() wasn’t called."""
    with pytest.raises(RuntimeError):
        Database.get_async_factory()


@pytest.mark.asyncio
async def test_initialize_creates_async_session():
    """
    initialize() should set up an async sessionmaker that produces
    sqlalchemy.ext.asyncio.AsyncSession instances.
    """
    # Note: sync URL is irrelevant here
    Database.initialize(database_url=ASYNC_URL, sync_database_url="sqlite:///:memory:")
    factory = Database.get_async_factory()
    session = factory()
    assert isinstance(session, AsyncSession)
    await session.execute(text("SELECT 1"))
    await session.close()


@pytest.mark.asyncio
async def test_initialize_idempotent_for_async():
    """
    A second call to initialize() must not replace the existing
    async sessionmaker (singleton behavior).
    """
    first_factory = Database.get_async_factory()
    Database.initialize(database_url=ASYNC_URL, sync_database_url="sqlite:///:memory:")
    second_factory = Database.get_async_factory()
    assert first_factory is second_factory

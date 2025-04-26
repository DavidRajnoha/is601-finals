# tests/test_database_sync.py

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Database

SYNC_URL = "sqlite:///:memory:"


def setup_module(module):
    """Reset sync engine and factory before tests."""
    Database._sync_engine = None
    Database._sync_session_factory = None


def test_sync_factory_uninitialized_raises():
    """get_sync_factory() should raise if initialize() wasn’t called."""
    with pytest.raises(RuntimeError):
        Database.get_sync_factory()


def test_initialize_creates_sync_session():
    """
    initialize() should set up a sync sessionmaker that produces
    sqlalchemy.orm.Session instances.
    """
    # Note: async URL is irrelevant here
    Database.initialize(database_url="sqlite+aiosqlite:///:memory:", sync_database_url=SYNC_URL)
    factory = Database.get_sync_factory()
    session = factory()
    assert isinstance(session, Session)
    session.execute(text("SELECT 1"))
    session.close()


def test_initialize_idempotent_for_sync():
    """
    A second call to initialize() must not replace the existing
    sync sessionmaker (singleton behavior).
    """
    first_factory = Database.get_sync_factory()
    Database.initialize(database_url="sqlite+aiosqlite:///:memory:", sync_database_url=SYNC_URL)
    second_factory = Database.get_sync_factory()
    assert first_factory is second_factory

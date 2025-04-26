from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Database:
    """Handles database connections and sessions."""
    _async_engine = None
    _async_session_factory = None

    _sync_engine = None
    _sync_session_factory = None

    @classmethod
    def initialize(cls, database_url: Optional[str], sync_database_url: Optional[str], echo: bool = False):
        """Initialize the async engine and sessionmaker."""
        if database_url and cls._async_engine is None:  # Ensure engine is created once
            cls._async_engine = create_async_engine(database_url, echo=echo, future=True)
            cls._async_session_factory = sessionmaker(
                bind=cls._async_engine, class_=AsyncSession, expire_on_commit=False, future=True
            )

        if sync_database_url and cls._sync_engine is None:
            cls._sync_engine = create_engine(
                sync_database_url, echo=echo, future=True
            )
            cls._sync_session_factory = sessionmaker(
                bind=cls._sync_engine,
                autocommit=False,
                autoflush=False,
                future=True,
            )

    @classmethod
    def get_async_factory(cls) -> sessionmaker:
            if cls._async_session_factory is None:
                raise RuntimeError("Async engine not initialized.")
            return cls._async_session_factory

    @classmethod
    def get_sync_factory(cls) -> sessionmaker:
        if cls._sync_session_factory is None:
            raise RuntimeError("Sync engine not initialized.")
        return cls._sync_session_factory


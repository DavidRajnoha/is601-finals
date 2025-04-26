"""
File: conftest.py for integration tests

Overview:
This Python test file utilizes pytest to manage database states and HTTP clients for testing a web application 
built with FastAPI and SQLAlchemy. It includes detailed fixtures to mock the testing environment, 
ensuring each test is run in isolation with a consistent setup.
"""
# Third-party imports
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
from faker import Faker

# Application-specific imports
from app.main import app
from app.database import Base, Database
from app.dependencies import get_db, get_settings


fake = Faker()

settings = get_settings()
TEST_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
TEST_SYNC_DATABASE_URL = settings.test_sync_database_url
engine = create_async_engine(TEST_DATABASE_URL, echo=settings.debug)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionScoped = scoped_session(AsyncTestingSessionLocal)


@pytest.fixture(scope="function")
async def async_client(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


async def _create_all_tables(engine):
    """
    Create all tables in the database according to the Base metadata.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def shared_memory_engine():
    """
    Provide a single in-memory SQLite engine for the entire test session.

    Uses `cache=shared` so that multiple connections see the same database,
    and `check_same_thread=False` to allow cross-thread async access.
    """
    in_memory_url = "sqlite+aiosqlite:///:memory:?cache=shared"
    engine = create_async_engine(
        in_memory_url,
        connect_args={"check_same_thread": False},
        future=True,
    )

    await _create_all_tables(engine)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function", autouse=True)
async def refresh_schema(shared_memory_engine):
    """
    Reset the database schema before each test:
      1. Drop all tables.
      2. Re-create all tables.
    """
    async with shared_memory_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield

@pytest.fixture(scope="function")
async def db_session(shared_memory_engine, refresh_schema):
    """
    Yield a fresh AsyncSession for each test, bound to the shared in-memory engine.
    """
    AsyncSessionFactory = sessionmaker(
        shared_memory_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with AsyncSessionFactory() as session:
        yield session
        await session.close()

"""
File: conftest.py for integration tests

Overview:
This Python test file utilizes pytest to manage database states and HTTP clients for testing a web application 
built with FastAPI and SQLAlchemy. It includes detailed fixtures to mock the testing environment, 
ensuring each test is run in isolation with a consistent setup.
"""
import os
# Standard library imports
from builtins import Exception, range, str
from datetime import timedelta
from unittest.mock import AsyncMock

# Third-party imports
import pytest
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


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    base = os.path.dirname(__file__)
    for item in items:
        if str(item.fspath).startswith(base):
            item.add_marker(pytest.mark.integration)


# this is what creates the http client for your api tests
@pytest.fixture(scope="function")
async def async_client(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    try:
        Database.initialize(settings.database_url, settings.test_sync_database_url)
    except Exception as e:
        pytest.fail(f"Failed to initialize the database: {str(e)}")

# this function setup and tears down (drops tales) for each test function, so you have a clean database for each test.
@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # you can comment out this line during development if you are debugging a single test
         await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()

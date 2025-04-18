"""
File: conftest.py for unit tests

Overview:
This file provides fixtures for unit tests that don't require database access.
These fixtures focus on mocking dependencies to allow isolated component testing.
"""

# Standard library imports
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from uuid import uuid4

# Application-specific imports
from app.models.user_model import User, UserRole
from app.utils.security import hash_password


@pytest.fixture
def mock_user():
    """Create a mock user without database dependency."""
    user_id = uuid4()
    return User(
        id=user_id,
        nickname="test_user",
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=UserRole.AUTHENTICATED,
        email_verified=True,
        is_locked=False,
        failed_login_attempts=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    session.add = AsyncMock()
    session.delete = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    service = AsyncMock()
    service.send_verification_email = AsyncMock()
    service.send_user_email = AsyncMock()
    return service 
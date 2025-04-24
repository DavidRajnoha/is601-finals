
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService
from app.models.user_model import User, UserRole
from app.utils.security import hash_password
import app.services.user_service as us_module
from app.celery.tasks import verify_email_task


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
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_create_enqueues_verify_task_if_not_verified(monkeypatch, mock_db_session, mock_user):
    """
    When email_verified=False, create() should:
      - generate a verification token,
      - commit the session,
      - enqueue the Celery task via verify_email_task.delay(user_id).
    """
    # Arrange: stub out user creation and token generation
    monkeypatch.setattr(
        UserService, "_create_user_in_db",
        AsyncMock(return_value=mock_user)
    )
    monkeypatch.setattr(
        us_module, "generate_verification_token",
        lambda: "static-token"
    )
    calls = []
    monkeypatch.setattr(
        verify_email_task, "delay",
        lambda uid: calls.append(uid)
    )

    # Ensure the user appears unverified
    mock_user.email_verified = False

    user = await UserService.create(mock_db_session, mock_user.__dict__)

    assert user is mock_user
    assert user.verification_token == "static-token"
    assert calls == [user.id]
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_skips_verify_task_if_already_verified(monkeypatch, mock_db_session, mock_user):
    """
    When email_verified=True, create() should neither generate a token
    nor enqueue any task, and should not commit.
    """
    # Arrange: stub out user creation
    monkeypatch.setattr(
        UserService, "_create_user_in_db",
        AsyncMock(return_value=mock_user)
    )
    calls = []
    monkeypatch.setattr(
        verify_email_task, "delay",
        lambda uid: calls.append(uid)
    )

    # Simulate already-verified user
    mock_user.email_verified = True

    user = await UserService.create(mock_db_session, mock_user.__dict__)

    assert user is mock_user
    assert user.verification_token is None
    assert calls == []
    mock_db_session.commit.assert_not_awaited()

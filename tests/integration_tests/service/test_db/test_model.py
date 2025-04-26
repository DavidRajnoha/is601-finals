# tests/integration/service_db/test_user_service.py
import pytest
from datetime import datetime, timezone

from app.services.user_service import UserService
from app.models.user_model import UserRole, User

@pytest.mark.asyncio
async def test_create_user_in_db_and_defaults(db_session):
    # Supply minimal data; UserService will handle nickname and role logic
    data = {"email": "bob@example.com", "password": "s3cr3t", "role": "ADMIN"}
    new_user: User = await UserService._create_user_in_db(db_session, data)

    # Persisted correctly
    assert new_user.id is not None
    assert new_user.email == "bob@example.com"

    # First-created user becomes ADMIN and is email_verified
    assert new_user.role == UserRole.ADMIN
    assert new_user.email_verified is True

    # Fetch via service to ensure get_by_email works
    fetched = await UserService.get_by_email(db_session, "bob@example.com")
    assert fetched.id == new_user.id
    assert fetched.nickname == new_user.nickname


@pytest.mark.asyncio
async def test_failed_login_attempts_increment(db_session, user):
    before = user.failed_login_attempts
    user.failed_login_attempts += 1
    await db_session.commit()
    await db_session.refresh(user)
    assert user.failed_login_attempts == before + 1


@pytest.mark.asyncio
async def test_last_login_timestamp_roundtrip(db_session, user):
    now = datetime.now(timezone.utc)
    user.last_login_at = now
    await db_session.commit()
    await db_session.refresh(user)

    assert user.last_login_at == now.replace()

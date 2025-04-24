# tests/test_account_tasks_unit.py
from contextlib import contextmanager

import pytest
from unittest.mock import MagicMock

from app.celery.tasks import verify_email_task
from app.models.user_model import User

@pytest.fixture
def fake_session(mock_user):
    """A fake sync session whose .get() returns our mock_user."""
    session = MagicMock()
    session.get.return_value = mock_user
    return session

@pytest.fixture
def fake_session_factory(fake_session):
    """
    A factory that yields our fake_session in a with-statement.
    """
    @contextmanager
    def _factory():
        yield fake_session
    return _factory

@pytest.fixture
def fake_email_service():
    """A fake email service with send_user_email() we can inspect."""
    return MagicMock()

def test_verify_email_task_injected(
    mock_user,
    fake_session_factory,
    fake_email_service
):
    """
    verify_email_task.run() should:
      - call session_factory() once
      - call session.get(User, user_id)
      - call email_svc.send_user_email(user)
      - return True
    """
    result = verify_email_task.run(
        mock_user.id,
        fake_email_service,
        fake_session_factory
    )

    assert result is True
    fake_session_factory().__enter__().get.assert_called_once_with(User, mock_user.id)    # fake_session_factory.return_value.get.assert_called_once_with(User, mock_user.id)
    fake_email_service.send_verification_email.assert_called_once_with(mock_user)
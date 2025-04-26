"""
Unit tests for Celery task functions in app.celery.tasks module.

These tests verify that the task functions correctly interact with their dependencies
and perform the expected operations.
"""
from contextlib import contextmanager

import pytest
from unittest.mock import MagicMock

from app.celery.tasks import (
    verify_email_task,
    account_locked_task,
    account_unlocked_task,
    role_upgrade_task,
    professional_status_upgrade_task
)
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
    Test that verify_email_task correctly uses injected dependencies.

    This test verifies that the verify_email_task:
    1. Retrieves the user from the database using the session factory
    2. Calls the email service to send a verification email
    3. Returns True upon successful completion

    Args:
        mock_user: Fixture providing a mock user object
        fake_session_factory: Fixture providing a factory that returns a mock database session
        fake_email_service: Fixture providing a mock email service
    """
    result = verify_email_task.run(
        mock_user.id,
        fake_email_service,
        fake_session_factory
    )

    assert result is True
    fake_session_factory().__enter__().get.assert_called_once_with(User, mock_user.id)
    fake_email_service.send_verification_email.assert_called_once_with(mock_user)

def test_account_locked_task_injected(
    mock_user,
    fake_session_factory,
    fake_email_service
):
    """
    Test that account_locked_task correctly uses injected dependencies.

    This test verifies that the account_locked_task:
    1. Retrieves the user from the database using the session factory
    2. Calls the email service to send an account locked notification email
    3. Returns True upon successful completion

    Args:
        mock_user: Fixture providing a mock user object
        fake_session_factory: Fixture providing a factory that returns a mock database session
        fake_email_service: Fixture providing a mock email service
    """
    result = account_locked_task.run(
        mock_user.id,
        fake_email_service,
        fake_session_factory
    )

    assert result is True
    fake_session_factory().__enter__().get.assert_called_once_with(User, mock_user.id)
    fake_email_service.send_account_locked_email.assert_called_once_with(mock_user)

def test_account_unlocked_task_injected(
    mock_user,
    fake_session_factory,
    fake_email_service
):
    """
    Test that account_unlocked_task correctly uses injected dependencies.

    This test verifies that the account_unlocked_task:
    1. Retrieves the user from the database using the session factory
    2. Calls the email service to send an account unlocked notification email
    3. Returns True upon successful completion

    Args:
        mock_user: Fixture providing a mock user object
        fake_session_factory: Fixture providing a factory that returns a mock database session
        fake_email_service: Fixture providing a mock email service
    """
    result = account_unlocked_task.run(
        mock_user.id,
        fake_email_service,
        fake_session_factory
    )

    assert result is True
    fake_session_factory().__enter__().get.assert_called_once_with(User, mock_user.id)
    fake_email_service.send_account_unlocked_email.assert_called_once_with(mock_user)

def test_role_upgrade_task_injected(
    mock_user,
    fake_session_factory,
    fake_email_service
):
    """
    Test that role_upgrade_task correctly uses injected dependencies.

    This test verifies that the role_upgrade_task:
    1. Retrieves the user from the database using the session factory
    2. Calls the email service to send a role upgrade notification email with the new role
    3. Returns True upon successful completion

    Args:
        mock_user: Fixture providing a mock user object
        fake_session_factory: Fixture providing a factory that returns a mock database session
        fake_email_service: Fixture providing a mock email service
    """
    new_role = "ADMIN"
    result = role_upgrade_task.run(
        mock_user.id,
        new_role,
        fake_email_service,
        fake_session_factory
    )

    assert result is True
    fake_session_factory().__enter__().get.assert_called_once_with(User, mock_user.id)
    fake_email_service.send_role_upgrade_email.assert_called_once_with(mock_user, new_role)

def test_professional_status_upgrade_task_injected(
    mock_user,
    fake_session_factory,
    fake_email_service
):
    """
    Test that professional_status_upgrade_task correctly uses injected dependencies.

    This test verifies that the professional_status_upgrade_task:
    1. Retrieves the user from the database using the session factory
    2. Calls the email service to send a professional status upgrade notification email
    3. Returns True upon successful completion

    Args:
        mock_user: Fixture providing a mock user object
        fake_session_factory: Fixture providing a factory that returns a mock database session
        fake_email_service: Fixture providing a mock email service
    """
    result = professional_status_upgrade_task.run(
        mock_user.id,
        fake_email_service,
        fake_session_factory
    )

    assert result is True
    fake_session_factory().__enter__().get.assert_called_once_with(User, mock_user.id)
    fake_email_service.send_professional_status_upgrade_email.assert_called_once_with(mock_user)

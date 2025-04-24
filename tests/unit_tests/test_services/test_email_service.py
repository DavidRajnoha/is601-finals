"""
Unit tests for the EmailService class in app.services.email_service module.

These tests verify that the EmailService correctly constructs email payloads,
renders templates, and sends emails through the SMTP client.
"""
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.services.email_service import EmailService
from app.models.user_model import User

@pytest.fixture
def mock_template_manager():
    tm = MagicMock()
    tm.render_template.return_value = "<html>Test email content</html>"
    return tm

@pytest.fixture
def email_service(mock_template_manager):
    service = EmailService(template_manager=mock_template_manager)
    service.smtp_client = MagicMock()
    return service

@pytest.fixture
def mock_user():
    uid = uuid4()
    return User(
        id=uid,
        nickname="test_user",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        verification_token="test-verification-token"
    )

def test_send_user_email(email_service):
    """
    Test that send_user_email correctly renders templates and sends emails.

    This test verifies that the send_user_email method:
    1. Calls the template manager to render the correct template with the provided user data
    2. Calls the SMTP client to send an email with the correct subject, HTML content, and recipient

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
    """
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "verification_url": "http://example.com/verify"
    }

    email_service.send_user_email(user_data, "email_verification")

    email_service.template_manager.render_template.assert_called_once_with(
        "email_verification", **user_data
    )
    email_service.smtp_client.send_email.assert_called_once_with(
        "Verify Your Account",
        "<html>Test email content</html>",
        "test@example.com"
    )

def test_send_user_email_invalid_type(email_service):
    """
    Test that send_user_email raises ValueError for invalid email types.

    This test verifies that the send_user_email method properly validates
    the email_type parameter and raises a ValueError with an appropriate
    error message when an invalid type is provided.

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
    """
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }

    with pytest.raises(ValueError, match="Invalid email type"):
        email_service.send_user_email(user_data, "invalid_type")

def test_send_verification_email_constructs_payload_and_calls(email_service, mock_user, monkeypatch):
    """
    Test that send_verification_email correctly builds the payload and calls send_user_email.

    This test verifies that the send_verification_email method:
    1. Constructs a verification URL using the server base URL and user information
    2. Creates a payload with the user's first name, email, and verification URL
    3. Calls send_user_email with the correct payload and email type

    The test patches the server base URL to a known value for predictable testing.

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
        mock_user: Fixture providing a mock user object
        monkeypatch: Pytest fixture for modifying environment/modules during testing
    """
    # Set a predictable server base URL for testing
    monkeypatch.setattr(
        "settings.config.settings.server_base_url",
        "http://testserver.com/"
    )

    email_service.send_user_email = MagicMock()

    email_service.send_verification_email(mock_user)

    email_service.send_user_email.assert_called_once()

    payload = email_service.send_user_email.call_args[0][0]
    expected_url = f"http://testserver.com/verify-email/{mock_user.id}/{mock_user.verification_token}"
    assert payload["verification_url"] == expected_url
    assert payload["name"] == mock_user.first_name
    assert payload["email"] == mock_user.email

def test_send_account_locked_email_constructs_payload_and_calls(email_service, mock_user):
    """
    Test that send_account_locked_email correctly builds the payload and calls send_user_email.

    This test verifies that the send_account_locked_email method:
    1. Creates a payload with the user's first name and email
    2. Calls send_user_email with the correct payload and 'account_locked' email type

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
        mock_user: Fixture providing a mock user object
    """
    email_service.send_user_email = MagicMock()

    email_service.send_account_locked_email(mock_user)

    email_service.send_user_email.assert_called_once()

    payload = email_service.send_user_email.call_args[0][0]
    assert payload["name"] == mock_user.first_name
    assert payload["email"] == mock_user.email

    email_type = email_service.send_user_email.call_args[0][1]
    assert email_type == 'account_locked'

def test_send_account_unlocked_email_constructs_payload_and_calls(email_service, mock_user):
    """
    Test that send_account_unlocked_email correctly builds the payload and calls send_user_email.

    This test verifies that the send_account_unlocked_email method:
    1. Creates a payload with the user's first name and email
    2. Calls send_user_email with the correct payload and 'account_unlocked' email type

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
        mock_user: Fixture providing a mock user object
    """
    email_service.send_user_email = MagicMock()

    email_service.send_account_unlocked_email(mock_user)

    email_service.send_user_email.assert_called_once()

    payload = email_service.send_user_email.call_args[0][0]
    assert payload["name"] == mock_user.first_name
    assert payload["email"] == mock_user.email

    email_type = email_service.send_user_email.call_args[0][1]
    assert email_type == 'account_unlocked'

def test_send_role_upgrade_email_constructs_payload_and_calls(email_service, mock_user):
    """
    Test that send_role_upgrade_email correctly builds the payload and calls send_user_email.

    This test verifies that the send_role_upgrade_email method:
    1. Creates a payload with the user's first name, email, and the new role
    2. Calls send_user_email with the correct payload and 'role_upgrade' email type

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
        mock_user: Fixture providing a mock user object
    """
    email_service.send_user_email = MagicMock()

    # Test with a specific role value
    new_role = "ADMIN"

    email_service.send_role_upgrade_email(mock_user, new_role)

    email_service.send_user_email.assert_called_once()

    payload = email_service.send_user_email.call_args[0][0]
    assert payload["name"] == mock_user.first_name
    assert payload["email"] == mock_user.email
    assert payload["new_role"] == new_role

    email_type = email_service.send_user_email.call_args[0][1]
    assert email_type == 'role_upgrade'

def test_send_professional_status_upgrade_email_constructs_payload_and_calls(email_service, mock_user):
    """
    Test that send_professional_status_upgrade_email correctly builds the payload and calls send_user_email.

    This test verifies that the send_professional_status_upgrade_email method:
    1. Creates a payload with the user's first name and email
    2. Calls send_user_email with the correct payload and 'professional_status_upgrade' email type

    Args:
        email_service: Fixture providing a configured EmailService with mock dependencies
        mock_user: Fixture providing a mock user object
    """
    email_service.send_user_email = MagicMock()

    email_service.send_professional_status_upgrade_email(mock_user)

    email_service.send_user_email.assert_called_once()

    payload = email_service.send_user_email.call_args[0][0]
    assert payload["name"] == mock_user.first_name
    assert payload["email"] == mock_user.email

    email_type = email_service.send_user_email.call_args[0][1]
    assert email_type == 'professional_status_upgrade'

# tests/test_email_service.py
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
    Test that send_user_email:
      - renders the correct template,
      - calls smtp_client.send_email with the right subject, html, and recipient.
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
    Sending with an invalid email_type should raise ValueError.
    """
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }

    with pytest.raises(ValueError, match="Invalid email type"):
        email_service.send_user_email(user_data, "invalid_type")

def test_send_verification_email_constructs_payload_and_calls(email_service, mock_user, monkeypatch):
    """
    Test that send_verification_email builds the correct payload and
    delegates to send_user_email.
    """
    # Patch the base URL
    monkeypatch.setattr(
        "settings.config.settings.server_base_url",
        "http://testserver.com/"
    )

    # Replace send_user_email with a MagicMock
    email_service.send_user_email = MagicMock()

    # Call the high-level method
    email_service.send_verification_email(mock_user)

    # It should call send_user_email exactly once
    email_service.send_user_email.assert_called_once()

    # Inspect the payload dict passed as the first positional argument
    payload = email_service.send_user_email.call_args[0][0]
    expected_url = f"http://testserver.com/verify-email/{mock_user.id}/{mock_user.verification_token}"
    assert payload["verification_url"] == expected_url
    assert payload["name"] == mock_user.first_name
    assert payload["email"] == mock_user.email

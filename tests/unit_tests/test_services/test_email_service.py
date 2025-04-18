import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.email_service import EmailService
from app.models.user_model import User
from uuid import uuid4


@pytest.fixture
def mock_template_manager():
    template_manager = MagicMock()
    template_manager.render_template.return_value = "<html>Test email content</html>"
    return template_manager


@pytest.fixture
def email_service(mock_template_manager):
    service = EmailService(template_manager=mock_template_manager)
    service.smtp_client = MagicMock()
    return service


@pytest.fixture
def mock_user():
    user_id = uuid4()
    return User(
        id=user_id,
        nickname="test_user",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        verification_token="test-verification-token"
    )


@pytest.mark.asyncio
async def test_send_user_email(email_service):
    """Test sending a user email."""
    # Arrange
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "verification_url": "http://example.com/verify"
    }
    
    # Act
    await email_service.send_user_email(user_data, "email_verification")
    
    # Assert
    email_service.template_manager.render_template.assert_called_once_with(
        "email_verification", **user_data
    )
    email_service.smtp_client.send_email.assert_called_once_with(
        "Verify Your Account", 
        "<html>Test email content</html>", 
        "test@example.com"
    )


@pytest.mark.asyncio
async def test_send_user_email_invalid_type(email_service):
    """Test sending a user email with an invalid email type."""
    # Arrange
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid email type"):
        await email_service.send_user_email(user_data, "invalid_type")


@pytest.mark.asyncio
async def test_send_verification_email(email_service, mock_user, monkeypatch):
    """Test sending a verification email."""
    # Patch the settings.server_base_url
    monkeypatch.setattr("settings.config.settings.server_base_url", "http://testserver.com/")
    
    # Mock the send_user_email method
    email_service.send_user_email = AsyncMock()
    
    # Act
    await email_service.send_verification_email(mock_user)
    
    # Assert
    email_service.send_user_email.assert_called_once()
    # Check that the verification URL was constructed correctly
    call_args = email_service.send_user_email.call_args[0][0]
    assert call_args["verification_url"] == f"http://testserver.com/verify-email/{mock_user.id}/test-verification-token"
    assert call_args["name"] == "Test"
    assert call_args["email"] == "test@example.com" 
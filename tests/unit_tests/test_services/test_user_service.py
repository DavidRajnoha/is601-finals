import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.user_service import UserService
from app.models.user_model import User, UserRole
from uuid import UUID, uuid4
from app.utils.security import hash_password
from datetime import datetime, timezone


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
    return session


@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    service = AsyncMock()
    service.send_verification_email = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_get_by_id_found(mock_db_session, mock_user):
    """Test retrieving a user by ID when the user exists."""
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = mock_user
    mock_db_session.execute.return_value = mock_result
    
    with patch.object(UserService, '_execute_query', return_value=mock_result):
        user = await UserService.get_by_id(mock_db_session, mock_user.id)
        
        assert user is not None
        assert user.id == mock_user.id
        assert user.email == mock_user.email


@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_db_session):
    """Test retrieving a user by ID when the user doesn't exist."""
    mock_db_session.execute.return_value = None
    
    with patch.object(UserService, '_execute_query', return_value=None):
        user = await UserService.get_by_id(mock_db_session, uuid4())
        
        assert user is None


@pytest.mark.asyncio
async def test_login_user_success(mock_db_session, mock_user):
    """Test successful user login."""
    # Arrange
    password = "password123"
    
    with patch.object(UserService, 'get_by_email', return_value=mock_user), \
         patch('app.utils.security.verify_password', return_value=True):
        
        # Act
        result = await UserService.login_user(mock_db_session, mock_user.email, password)
        
        # Assert
        assert result is not None
        assert result.id == mock_user.id
        assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_login_user_incorrect_password(mock_db_session, mock_user):
    """Test login with incorrect password."""
    # Arrange
    password = "wrong_password"
    
    with patch.object(UserService, 'get_by_email', return_value=mock_user), \
         patch('app.utils.security.verify_password', return_value=False):
        
        # Act
        result = await UserService.login_user(mock_db_session, mock_user.email, password)
        
        # Assert
        assert result is None
        assert mock_db_session.commit.called  # Failed login increments counter


@pytest.mark.asyncio
async def test_verify_email_with_token_success(mock_db_session, mock_user):
    """Test successful email verification with token."""
    # Arrange
    token = "valid_token"
    mock_user.verification_token = token
    
    with patch.object(UserService, 'get_by_id', return_value=mock_user):
        # Act
        result = await UserService.verify_email_with_token(mock_db_session, mock_user.id, token)
        
        # Assert
        assert result is True
        assert mock_user.email_verified is True
        assert mock_user.verification_token is None
        assert mock_user.role == UserRole.AUTHENTICATED
        assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_verify_email_with_token_invalid(mock_db_session, mock_user):
    """Test failed email verification with invalid token."""
    token = "valid_token"
    invalid_token = "invalid_token"
    mock_user.verification_token = token
    
    with patch.object(UserService, 'get_by_id', return_value=mock_user):
        result = await UserService.verify_email_with_token(mock_db_session, mock_user.id, invalid_token)
        
        assert result is False
        assert mock_user.email_verified is True  # Unchanged

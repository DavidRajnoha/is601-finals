import pytest
from app.utils.security import hash_password, verify_password, generate_verification_token


def test_hash_password():
    """Test that hashing password returns a bcrypt hashed string."""
    password = "secure_password"
    hashed = hash_password(password)
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed.startswith('$2b$')


def test_hash_password_different_rounds():
    """Test that hashing with different rounds produces different results."""
    password = "secure_password"
    hashed1 = hash_password(password, rounds=10)
    hashed2 = hash_password(password, rounds=12)
    assert hashed1 != hashed2


def test_verify_password_correct():
    """Test verifying the correct password."""
    password = "secure_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test verifying the incorrect password."""
    password = "secure_password"
    hashed = hash_password(password)
    wrong_password = "incorrect_password"
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_invalid_hash():
    """Test verifying a password against an invalid hash format."""
    with pytest.raises(ValueError):
        verify_password("secure_password", "invalid_hash_format")


def test_verify_password_edge_cases():
    """Test verifying passwords with edge cases."""
    password = " "
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("not empty", hashed) is False


def test_generate_verification_token():
    """Test that verification token is generated with expected format."""
    token = generate_verification_token()
    assert isinstance(token, str)
    assert len(token) > 16  # Token should be reasonably long
    
    # Test uniqueness
    token2 = generate_verification_token()
    assert token != token2  # Tokens should be unique 
from builtins import RuntimeError, ValueError, isinstance, str
import pytest
from app.utils.security import (
    hash_password,
    verify_password,
    generate_verification_token,
)


def test_hash_password():
    """Test that hashing password returns a bcrypt hashed string."""
    password = "secure_password"
    hashed = hash_password(password)
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed.startswith('$2b$')


def test_hash_password_with_different_rounds():
    """Test hashing with different cost factors."""
    password = "secure_password"
    hashed_10 = hash_password(password, 10)
    hashed_12 = hash_password(password, 12)
    assert hashed_10 != hashed_12, "Hashes should differ with different cost factors"


@pytest.mark.parametrize("password", [
    "",
    " ",
    "a" * 100,  # Long password
])
def test_hash_password_edge_cases(password):
    """Test hashing various edge-case passwords."""
    hashed = hash_password(password)
    assert isinstance(hashed, str) and hashed.startswith('$2b$'), "Should handle edge cases properly"


def test_hash_password_internal_error(monkeypatch):
    """Test proper error handling when an internal bcrypt error occurs."""
    def mock_gensalt(rounds):
        raise RuntimeError("Simulated internal error")

    monkeypatch.setattr("bcrypt.gensalt", mock_gensalt)
    with pytest.raises(ValueError):
        hash_password("test")


def test_verify_password_correct():
    """Test verifying the correct password."""
    password = "secure_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test verifying the incorrect password."""
    password = "secure_password"
    hashed = hash_password(password)
    assert verify_password("incorrect_password", hashed) is False


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
    token1 = generate_verification_token()
    assert isinstance(token1, str)
    assert len(token1) > 16, "Token should be reasonably long"

    token2 = generate_verification_token()
    assert token1 != token2, "Tokens should be unique"

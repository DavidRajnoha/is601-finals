import re
from unittest.mock import patch
from app.utils.nickname_gen import generate_nickname


def test_generate_nickname_format():
    """Test that the generated nickname follows the expected format."""
    nickname = generate_nickname()
    
    # Check format adjective_animal_number
    pattern = r'^[a-z]+_[a-z]+_\d+$'
    assert re.match(pattern, nickname), f"Nickname '{nickname}' does not match expected pattern"


def test_generate_nickname_uniqueness():
    """Test that multiple generated nicknames are likely to be unique."""
    nicknames = [generate_nickname() for _ in range(10)]
    unique_nicknames = set(nicknames)
    
    # With random selection from lists, it's possible but unlikely to get duplicates
    assert len(unique_nicknames) >= 9, "Generated nicknames should generally be unique"


@patch('random.choice')
@patch('random.randint')
def test_generate_nickname_deterministic(mock_randint, mock_choice):
    """Test nickname generation with mocked random functions for deterministic result."""
    # Mock the random functions
    mock_choice.side_effect = lambda x: x[0]  # Always return first item
    mock_randint.return_value = 123
    
    # Expected result based on the implementation and our mocks
    expected = "clever_panda_123"
    
    # Generate nickname with mocked random functions
    result = generate_nickname()
    
    # Assert the result matches expected
    assert result == expected, f"Expected '{expected}' but got '{result}'" 
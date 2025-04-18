# Unit Tests

This directory contains unit tests that can be run without any external dependencies like databases. These tests focus on testing individual components in isolation, using mocks for dependencies.

## Benefits of Unit Tests

- **Fast execution**: Unit tests run quickly since they don't require database setup
- **No external dependencies**: Can be run without setting up a database or other external services
- **Focused testing**: Tests the logic of individual functions without the complexity of integration
- **Easy to maintain**: Easier to identify what broke when tests fail
- **Support TDD**: Ideal for Test-Driven Development workflows

## Running Unit Tests

To run only the unit tests, use Poetry:

```bash
poetry run pytest tests/unit_tests -v
```

## Test Structure

The tests are organized into two main directories:

- `tests/unit_tests/` - Contains tests that don't require a database or external services
- `tests/integration_tests/` - Contains tests that need a database connection and test component interactions

Each directory has its own `conftest.py` file with the appropriate fixtures:

- Unit tests use mocked databases and dependencies
- Integration tests configure a real test database for each test

## Writing New Unit Tests

When writing new unit tests, follow these guidelines:

1. Use mocks for external dependencies (database, email services, etc.)
2. Test one function or method at a time
3. Use descriptive test names that explain what's being tested
4. Use fixtures from `tests/unit_tests/conftest.py`
5. Organize tests by module or functionality

Example structure:

```python
# Test for a specific function
@pytest.mark.asyncio  # For async tests
async def test_function_name_scenario(mock_db_session, mock_user):
    # Arrange - Set up test data and mocks
    # Act - Call the function being tested
    # Assert - Check the results
```

## Current Unit Test Coverage

The current set of unit tests covers:

- `security.py` - Password hashing, verification, and token generation
- `nickname_gen.py` - Nickname generation
- `user_service.py` - Core user service functionality with mocked database

## Differences from Integration Tests

Integration tests in the parent directory use an actual test database and test the interaction between multiple components. Unit tests focus on testing individual components in isolation. 
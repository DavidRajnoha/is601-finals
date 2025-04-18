# Test Structure

This project contains two types of tests:

1. **Unit Tests**: Fast, isolated tests that don't require external dependencies
2. **Integration Tests**: Tests that verify interactions between components using a test database

## Directory Structure

```
tests/
├── conftest.py               # Minimal configuration for all tests
├── __init__.py
├── integration_tests/        # Tests requiring database or external services
│   ├── conftest.py           # Database setup and fixtures for integration tests
│   ├── __init__.py
│   ├── test_api/             # Tests for API endpoints
│   ├── test_event_based/     # Tests for event-based functionality
│   ├── test_models/          # Tests for database models
│   ├── test_schemas/         # Tests for Pydantic schemas
│   └── test_services/        # Tests for services with database interactions
└── unit_tests/               # Tests that run without external dependencies
    ├── conftest.py           # Mock fixtures for unit tests
    ├── __init__.py
    ├── README.md             # Specific guidance for unit tests
    ├── test_email_service.py # Tests for email service
    ├── test_nickname_gen.py  # Tests for nickname generation
    ├── test_security.py      # Tests for security utilities
    ├── test_template_manager.py # Tests for template manager
    └── test_user_service.py  # Tests for user service with mocked DB
```

## Running Tests

### Unit Tests

Run only the unit tests (no database required) using Poetry:

```bash
poetry run pytest tests/unit_tests -v
```

### Integration Tests

Run integration tests using Poetry (requires a running database configured via environment variables):

```bash
poetry run pytest tests/integration_tests -v
```

Alternatively, run integration tests within the Docker environment (manages database setup):

```bash
# Ensure Docker Compose services are running (docker-compose up -d)
docker-compose exec app poetry run pytest tests/integration_tests -v
```

### All Tests

Run all tests using Poetry (unit tests first, then integration tests):

```bash
poetry run pytest -v
```

## Using Markers

You can use pytest markers to run specific types of tests:

```bash
# Run only unit tests
poetry run pytest -m unit -v

# Run only integration tests
poetry run pytest -m integration -v
```

## Testing Philosophy

1. **Unit Tests**: Focus on testing individual functions or classes in isolation. They use mocks to avoid external dependencies like databases.

2. **Integration Tests**: Test how components work together with real database interactions, either locally configured or via Docker Compose.

This split approach provides the benefits of both:
- Fast unit tests that can be run locally with no setup
- Comprehensive integration tests to verify the application works as a whole 
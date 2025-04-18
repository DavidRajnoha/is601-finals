"""
Main conftest.py for test configuration.

This file is minimal since tests are now divided into:
- unit_tests/ - For tests that don't require external dependencies
- integration_tests/ - For tests that require a database and other external services

Each directory has its own conftest.py with appropriate fixtures.
"""

import pytest

# This hook helps pytest understand how to collect and run tests
def pytest_configure(config):
    """
    Configure the pytest environment.
    This runs at the beginning of a pytest session.
    """
    # Register custom markers
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test that requires database or external services")

    # Nothing else is needed here - fixtures are defined in their respective conftest.py files:
    # - tests/unit_tests/conftest.py - For unit test fixtures
    # - tests/integration_tests/conftest.py - For integration test fixtures

#!/bin/bash

echo "Running integration tests using Docker Compose"
docker-compose exec fastapi python -m pytest /myapp/tests/integration_tests

# Exit with the status of the pytest command
exit $?
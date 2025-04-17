# Define a base stage with a Debian Bookworm base image that includes the latest glibc update
FROM python:3.13-bookworm as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    POETRY_VERSION=2.1.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY=true \
    QR_CODE_DIR=/myapp/qr_codes

WORKDIR /myapp

# Update system and specifically upgrade libc-bin to the required security patch version
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get install -y libc-bin=2.36-9+deb12u10 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copy only pyproject.toml and poetry.lock* to leverage Docker layer caching
COPY pyproject.toml poetry.lock* ./

# Debug: Check the content of pyproject.toml
RUN cat pyproject.toml

# Install Python dependencies in .venv
RUN poetry install --no-root

# Debug: List all files in the virtual environment bin directory
RUN ls -la .venv/bin/

# Define a second stage for the runtime, using the same Debian Bookworm slim image
FROM python:3.13-slim-bookworm as final

# Upgrade libc-bin in the final stage to ensure security patch is applied
RUN apt-get update && apt-get install -y libc-bin=2.36-9+deb12u10 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the base stage
COPY --from=base /myapp/.venv /.venv

# Debug: List all files in the virtual environment bin directory in the final image
RUN ls -la /.venv/bin/

# Set environment variable to ensure all python commands run inside the virtual environment
ENV PATH="/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    QR_CODE_DIR=/myapp/qr_codes

# Debug: Print the PATH environment variable
RUN echo $PATH

# Debug: Try to locate the uvicorn executable
RUN which uvicorn || echo "uvicorn not found in PATH"

# Set the working directory
WORKDIR /myapp

# Create and switch to a non-root user
RUN useradd -m myuser
USER myuser

# Copy application code with appropriate ownership
COPY --chown=myuser:myuser . .

# Inform Docker that the container listens on the specified port at runtime.
EXPOSE 8000

RUN which python && python -c "import sys; print(sys.executable); import uvicorn; print(uvicorn.__file__)"

# Use ENTRYPOINT to specify the executable when the container starts.
ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
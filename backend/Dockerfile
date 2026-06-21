# === MAX VPS Backend Dockerfile ===
# Multi-stage build для маленького образа

# === Stage 1: Build dependencies ===
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps для asyncpg, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.4

# Copy deps files
COPY pyproject.toml ./

# Configure poetry: no venv, install only main deps
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# === Stage 2: Runtime ===
FROM python:3.11-slim AS runtime

WORKDIR /app

# System deps (для asyncpg + healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash maxvps

# Copy installed deps из builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

# Permissions
RUN chown -R maxvps:maxvps /app
USER maxvps

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

EXPOSE 8000

# Default: uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

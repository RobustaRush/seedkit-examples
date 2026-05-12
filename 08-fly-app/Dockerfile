# syntax=docker/dockerfile:1
# django-bolt ships no aarch64-linux wheel — compile from source on the base
# stage so both dev and prod targets inherit a prebuilt wheel in the uv cache.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


FROM base AS dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM base AS builder
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.12-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

USER django

# collectstatic runs at deploy time (fly.toml release_command) because
# S3 requires real credentials unavailable at build time.

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

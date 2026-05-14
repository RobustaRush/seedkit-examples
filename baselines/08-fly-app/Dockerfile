# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

# django-bolt ships no aarch64-linux wheel — build from source on that arch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# collectstatic runs at deploy time (fly.toml release_command) because S3
# credentials are not available at build time.


FROM python:3.12-slim-bookworm AS prod

ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA} \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

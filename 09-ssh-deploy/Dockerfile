# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

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

RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    /opt/venv/bin/python manage.py collectstatic --noinput


FROM python:3.12-slim-bookworm AS prod
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

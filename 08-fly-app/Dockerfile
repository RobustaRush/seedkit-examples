# syntax=docker/dockerfile:1

# ── base: shared dep install (uv available here) ───────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
# BuildKit cache mount keeps the uv wheel cache across stages so packages
# that build native extensions (e.g. django-bolt via maturin) are compiled
# once and reused by the builder stage.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


# ── dev target: runserver, bind-mounted source ──────────────────────────────
FROM base AS dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# ── builder: prod deps only (no dev group) ──────────────────────────────────
FROM base AS builder
# Reuses the uv cache populated by the base stage — no Rust recompilation.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ── prod target: slim runtime, no uv binary ─────────────────────────────────
FROM python:3.12-slim-bookworm AS prod

ARG GIT_SHA=unknown
ENV PATH="/app/.venv/bin:$PATH" \
    GIT_SHA=${GIT_SHA}

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /app /app

# S3 storage: collectstatic runs at deploy time (fly.toml release_command),
# not at build time — bucket credentials must not enter the build context.

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

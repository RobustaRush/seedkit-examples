# ── builder ──────────────────────────────────────────────────────────────────
# Full bookworm image + build tools so django-bolt compiles on aarch64-linux.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── dev ──────────────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS dev

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ── prod (slim runtime) ───────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS prod

ENV PATH="/app/.venv/bin:$PATH"

ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA}

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /app /app

USER django

# collectstatic is skipped — S3 receives assets at deploy time (see fly.toml release_command)
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "2"]

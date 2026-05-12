# Builder: full uv image + build tools (needed for django-bolt Rust extension
# which has no aarch64-linux wheel — compiles from source on Apple Silicon).
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

# collectstatic is skipped here — S3 storage needs real credentials at
# deploy time. Run via fly.toml [deploy] release_command instead.


# Dev target: full toolchain, bind-mounts for live reload.
FROM builder AS dev

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# Slim runtime: no uv binary, ~100-200 MB lighter than the builder.
FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /app /app

USER django


# Prod target: slim runtime with gunicorn.
FROM runtime AS prod

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

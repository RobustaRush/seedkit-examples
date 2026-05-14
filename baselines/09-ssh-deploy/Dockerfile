# syntax=docker/dockerfile:1
# ── Stage 1: dependency builder (uv + Python 3.12) ───────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Install production dependencies only
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

# Copy source and install the project itself
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# System deps for psycopg (libpq) only
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtualenv from builder — no pip/uv needed at runtime
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-"]

# ─── builder stage ────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ─── dev stage ────────────────────────────────────────────────────────────────
FROM builder AS dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ─── runtime stage (slim — no uv binary) ──────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /app /app

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

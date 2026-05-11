FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen


FROM base AS dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM python:3.12-slim-bookworm AS prod

ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=base --chown=django:django /app /app

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

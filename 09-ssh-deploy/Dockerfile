FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

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


FROM base AS prod

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django
RUN chown -R django:django /app

RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    python manage.py collectstatic --noinput

USER django
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]

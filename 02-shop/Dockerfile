# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-editable 2>/dev/null || uv sync --no-dev --no-editable

# ── node/css builder ──────────────────────────────────────────────────────────
FROM node:22-slim AS css-builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --include=dev 2>/dev/null || npm install

COPY frontend ./frontend
COPY templates ./templates
COPY pages ./pages
COPY users ./users

RUN npx @tailwindcss/cli -i frontend/input.css -o static/css/tailwind.css --minify

# ── runtime ───────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

RUN addgroup --system django && adduser --system --ingroup django django

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=django:django . .
COPY --from=css-builder --chown=django:django /app/static/css/tailwind.css ./static/css/tailwind.css

RUN DJANGO_SECRET_KEY=build-placeholder \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --noinput

USER django

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

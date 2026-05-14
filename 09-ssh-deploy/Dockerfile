# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv export --no-dev --no-hashes -o requirements.txt && \
    pip install --no-cache-dir -r requirements.txt --target /deps

# --- runtime ---
FROM python:3.12-slim-bookworm AS prod

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/deps \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Dummy key only used during collectstatic at build time — overridden at runtime
ARG DJANGO_SECRET_KEY=build-time-dummy-not-used-in-prod

RUN useradd --no-create-home --no-log-init --shell /bin/false app

WORKDIR /app

COPY --from=builder /deps /deps

COPY . .

RUN DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
    DATABASE_URL="sqlite:////tmp/build.sqlite3" \
    python -m django collectstatic --noinput

USER app

EXPOSE 8000

CMD ["python", "-m", "gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]

## Prompt

```
/seedkit

Project name: 08-fly-app
Purpose: production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

Settings layout: split.
Database: PostgreSQL.
Postgres location: Postgres-in-Docker (`db` service alongside `redis` and `minio` in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: `django-mail-auth` (passwordless magic-link).
Structured logging: no.
Task runner: mise.
Add-ons:
  - redis
  - tasks: Celery
  - storage: S3-compatible (MinIO locally, real S3 in prod)
  - analytics: Google Analytics 4 (GA4)
  - email: anymail (Postmark provider). Install `django-anymail[postmark]`; set `EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"` only when not DEBUG; gate `POSTMARK_SERVER_TOKEN` from env. Wire `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`. Console backend stays as the `EMAIL_URL` fallback in dev. (django-mail-auth needs working email to send magic links.) Also include the Anymail webhook URL (`path("anymail/", include("anymail.urls"))`) and `ANYMAIL["WEBHOOK_SECRET"]`.
  - CORS: no.
  - REST API: `django-bolt` **with fast-path settings opt-in** (`uv add django-bolt`). Add `django_bolt` to `INSTALLED_APPS` in `base.py`. Create `config/settings/bolt.py` that imports from `base` and strips `SessionMiddleware`, `MessageMiddleware`, `CsrfViewMiddleware`, `AuthenticationMiddleware`, `WhiteNoiseMiddleware` from `MIDDLEWARE` and `django.contrib.admin`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles` from `INSTALLED_APPS`; sets `TEMPLATES = []` and `ROOT_URLCONF = 'config.urls_bolt'`. Create `config/urls_bolt.py` (API-only; no admin / accounts). Create an `api` app (`uv run manage.py startapp api`) with `api/api.py` exposing `BoltAPI()`, a single `GET /users/{user_id}` async handler returning a `msgspec.Struct` (`id`, `username`) populated via `await User.objects.aget(id=user_id)`. `runserver`/`gunicorn` keep using `config.settings.local` / `production`; `runbolt` runs against `config.settings.bolt`.
  - Frontend: none.
  - Auth hardening: `django-axes` (yes), 2FA (no).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings
  - CSP via `django-csp`: yes
  - error reporting: GlitchTip via sentry-sdk
  - GDPR: PII scrubbing in error reports, retention defaults, user data export/delete views
  - CI: GitHub Actions test workflow
  - deploy target: Fly.io managed (use `[processes]` for web + worker + bolt; the `bolt` process runs `manage.py runbolt` with `DJANGO_SETTINGS_MODULE=config.settings.bolt`)
  - production Dockerfile: multi-stage (builder + slim runtime)

Run the foundation + boot check locally. Generate `Dockerfile`, `fly.toml`, `.github/workflows/test.yml`. Verify `docker build .` succeeds and the runtime stage uses `python:3.12-slim-bookworm`.
```

---

# 08-fly-app

Production Django app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (psycopg3) |
| Cache / broker | Redis |
| Task queue | Celery |
| Storage | S3-compatible (MinIO locally, AWS S3 in prod) |
| Auth | django-mail-auth (passwordless magic-link) |
| Auth hardening | django-axes |
| Email | anymail + Postmark (console in dev) |
| Analytics | Google Analytics 4 (gated — only fires in prod with `ANALYTICS_ID` set) |
| REST API | django-bolt (`GET /users/{id}`) |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Types | pyright + django-stubs |
| Task runner | mise |
| Error reporting | GlitchTip (sentry-sdk) |
| CSP | django-csp |
| Deploy | Fly.io (web + worker + bolt processes) |

## Local setup

```sh
# Copy and fill in the env file
cp .env.example .env

# Start local services (PostgreSQL, Redis, MinIO)
docker compose up -d --wait

# Install dependencies
mise run install   # or: uv sync

# Run migrations
mise run migrate

# Create a superuser
mise run superuser

# Start Django
mise run dev

# Start Celery worker (separate terminal)
mise run worker
```

The magic-link login is at <http://127.0.0.1:8000/accounts/login/> — in dev, the link is printed to the `runserver` stdout.

## Common tasks

| Task | Command |
|---|---|
| Run dev server | `mise run dev` |
| Run migrations | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Django shell | `mise run shell` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Celery worker | `mise run worker` |
| Deploy to Fly | `mise run deploy` |

Without mise: use `uv run manage.py <cmd>` or `uv run celery -A config worker -l info`.

## django-bolt fast-path API

The Bolt API runs as a separate process against stripped settings (`config.settings.bolt`):

```sh
# Dev — separate terminal
DJANGO_SETTINGS_MODULE=config.settings.bolt uv run manage.py runbolt --dev --port 8002

# Test the user endpoint
curl http://127.0.0.1:8002/users/1

# Bolt settings do NOT include admin / sessions / messages / staticfiles
```

In production Fly.io runs three processes: `web` (gunicorn), `worker` (Celery), and `bolt` (runbolt on port 8002).

## Health checks

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Liveness — process alive, no external deps |
| `GET /readyz` | Readiness — database reachable |

## GDPR management commands

```sh
uv run manage.py export_user_data <user_id>   # JSON dump to stdout
uv run manage.py delete_user_data  <user_id>   # atomic delete
```

## Deploy to Fly.io

```sh
fly launch --no-deploy
fly postgres create && fly postgres attach <db-name>
fly redis create && fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=<your-app>.fly.dev \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.fly.dev \
    POSTMARK_SERVER_TOKEN=<token> \
    ANYMAIL_WEBHOOK_SECRET=<secret> \
    AWS_ACCESS_KEY_ID=<key> \
    AWS_SECRET_ACCESS_KEY=<secret> \
    AWS_STORAGE_BUCKET_NAME=<bucket> \
    AWS_S3_REGION_NAME=us-east-1 \
    SENTRY_DSN=<dsn>
mise run deploy   # or: fly deploy
```

The `release_command` in `fly.toml` runs `python manage.py migrate && python manage.py collectstatic --noinput` before the new version goes live.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

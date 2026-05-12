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

Production Django app deployed to Fly.io with multi-stage Docker image and S3-compatible object storage.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (psycopg3) |
| Cache / broker | Redis (django-redis + Celery) |
| Storage | S3-compatible (MinIO locally, AWS S3 / R2 in prod) |
| Auth | django-mail-auth (passwordless magic-link) + django-axes |
| REST API | django-bolt (fast-path) |
| Email | django-anymail (Postmark in prod, console in dev) |
| Analytics | Google Analytics 4 |
| Error tracking | GlitchTip / sentry-sdk |
| Linting | Ruff |
| Tests | pytest + pytest-django |
| Type checking | pyright + django-stubs |
| Task runner | mise |
| Deploy | Fly.io |

## Setup

```sh
# copy env and start local services
cp .env.example .env   # fill in DJANGO_SECRET_KEY
docker compose up -d --wait

# install deps and run migrations
mise run install
mise run migrate

# create superuser and start servers
mise run superuser
mise run dev          # Django on :8000
mise run worker       # Celery worker
mise run bolt         # Bolt API on :8001 (separate terminal)
```

## Commands

| Command | What it does |
|---|---|
| `mise run install` | `uv sync` |
| `mise run dev` | `uv run manage.py runserver` |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run superuser` | `uv run manage.py createsuperuser` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run worker` | `uv run celery -A config worker -l info` |
| `mise run bolt` | Bolt API server (`DJANGO_SETTINGS_MODULE=config.settings.bolt`) |
| `mise run deploy` | `fly deploy` |

Without mise: use the `uv run …` commands directly.

## Bolt API

django-bolt runs a separate Rust-powered HTTP server. Routes:

- `GET /users/{user_id}` — returns `{"id": …, "username": "…"}` (msgspec)

Start with `mise run bolt` (port 8001 in dev). In production, the `bolt` process in `fly.toml` runs on port 8002.

## GDPR

```sh
uv run manage.py export_user_data <user_id>
uv run manage.py delete_user_data <user_id>
```

## Deploy to Fly.io

```sh
fly launch --no-deploy
fly postgres create && fly postgres attach <db-name>
fly redis create && fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=<your-fly-hostname> \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-fly-hostname> \
    EMAIL_URL=consolemail:// \
    DEFAULT_FROM_EMAIL=no-reply@example.com
mise run deploy
```

`fly deploy` triggers the release command (`python manage.py migrate && python manage.py collectstatic --noinput`) before switching traffic.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

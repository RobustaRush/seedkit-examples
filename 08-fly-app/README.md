## Prompt

```
/seedkit-slim

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

Production Django app deployed to Fly.io with a slim multi-stage Docker image and S3-compatible object storage.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL (psycopg3) |
| Cache / Broker | Redis (django-redis, Celery) |
| Storage | S3 / MinIO (django-storages) |
| Auth | django-mail-auth (magic link) + django-axes |
| Email | django-anymail (Postmark in prod, console in dev) |
| API | django-bolt (fast-path ASGI) |
| CSP | django-csp 4.0 |
| Error reporting | sentry-sdk → GlitchTip |
| Deploy | Fly.io (web + worker + bolt processes) |
| Lint | Ruff |
| Types | pyright + django-stubs |
| Tests | pytest + pytest-django |
| Tasks | mise |

## Local development

```bash
# Start services
docker compose up -d --wait

# Run migrations
mise run migrate

# Start web server
mise run dev

# Start Celery worker
mise run worker

# Start Bolt API
mise run bolt

# Run tests
mise run test

# Type check
mise run typecheck
```

## Key URLs

| URL | Description |
|---|---|
| `/admin/` | Django admin |
| `/accounts/login/` | Magic-link login |
| `/accounts/logout/` | Logout |
| `/healthz` | Liveness probe (returns `ok`) |
| `/readyz` | Readiness probe (returns `ready`) |
| `http://localhost:8001/users/{id}` | Bolt API — get user |
| `http://localhost:8001/docs` | Bolt OpenAPI docs |

## Environment

Copy `.env` and fill in production values. Required in production:
- `SECRET_KEY` — long random string
- `DATABASE_URL` — postgres URL
- `REDIS_URL` — redis URL
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`
- `POSTMARK_SERVER_TOKEN`
- `ANYMAIL_WEBHOOK_SECRET`
- `GLITCHTIP_DSN` — GlitchTip project DSN

## Deploy (Fly.io)

```bash
fly launch --no-deploy
fly secrets set SECRET_KEY=... DATABASE_URL=... REDIS_URL=... ...
fly deploy
```

Processes configured in `fly.toml`:
- `web` — gunicorn (Django WSGI)
- `worker` — Celery worker
- `bolt` — django-bolt API (`DJANGO_SETTINGS_MODULE=config.settings.bolt`)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

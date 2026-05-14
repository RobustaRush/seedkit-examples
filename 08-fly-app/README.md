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

Production Django app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL 16 |
| Cache / broker | Redis 7 |
| Task queue | Celery |
| Object storage | S3 (MinIO locally) |
| Auth | django-mail-auth (passwordless magic-link) |
| Brute-force protection | django-axes |
| Email | django-anymail (Postmark in prod, console in dev) |
| API (fast-path) | django-bolt |
| Analytics | Google Analytics 4 |
| CSP | django-csp |
| Error reporting | sentry-sdk → GlitchTip |
| Lint | Ruff |
| Types | Pyright + django-stubs |
| Tests | pytest + pytest-django |
| Tasks | mise |
| Deploy | Fly.io (multi-process) |

## Setup

```sh
cp .env.example .env   # fill in DJANGO_SECRET_KEY
docker compose up -d --wait
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Key commands

```sh
mise run dev           # Django runserver (port 8000)
mise run worker        # Celery worker
mise run bolt          # Bolt API server (port 8001, fast-path settings)
mise run migrate
mise run test
mise run lint
mise run typecheck
```

## Settings layout

| File | Purpose |
|---|---|
| `config/settings/base.py` | All shared settings |
| `config/settings/local.py` | Dev overrides (console email, DB from env) |
| `config/settings/production.py` | Prod hardening (Postmark, Sentry, HSTS) |
| `config/settings/bolt.py` | Fast-path: strips session/admin/static apps |

## Bolt API

Runs against `config.settings.bolt` which strips session middleware, admin, messages, staticfiles, and CSR token middleware. The Celery worker and `runserver` always use `local` or `production`.

```sh
# Dev
DJANGO_SETTINGS_MODULE=config.settings.bolt uv run manage.py runbolt --dev --port 8001
# OpenAPI docs: http://127.0.0.1:8001/docs
```

## Deploy to Fly.io

```sh
fly launch --copy-config --no-deploy
fly secrets set DJANGO_SECRET_KEY=... DATABASE_URL=... REDIS_URL=... \
    POSTMARK_SERVER_TOKEN=... GLITCHTIP_DSN=... \
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_STORAGE_BUCKET_NAME=... \
    ANYMAIL_WEBHOOK_SECRET=...
fly deploy
```

The `fly.toml` runs three process groups: `web` (gunicorn), `worker` (celery), `bolt` (runbolt on port 8001).

## GDPR

- `GET /gdpr/export/` — download your data as JSON (login required)
- `POST /gdpr/delete/` — delete your account (login required)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

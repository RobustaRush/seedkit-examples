## Prompt

```
/seedkit

Project name: 08-fly-app
Purpose: production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

Settings layout: split.
Database: PostgreSQL.
Local dev mode: docker-compose (web + db + redis + minio).
Docker structure: override (one multi-stage `Dockerfile` with `dev`/`prod` targets, `docker-compose.yml` + `docker-compose.override.yml`).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: `django-mail-auth` (passwordless magic-link).
Structured logging: no.
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

Production Django app deployed to Fly.io with S3-compatible object storage.

## Stack

- Django 6 · PostgreSQL · Redis
- Auth: `django-mail-auth` (passwordless magic-link) · `django-axes` (lockout)
- Tasks: Celery (Redis broker)
- Storage: S3-compatible (MinIO locally, AWS S3 / R2 in prod)
- Email: `django-anymail` / Postmark in prod; console in dev
- REST API: `django-bolt` (fast-path bolt settings, separate port)
- Analytics: Google Analytics 4
- Security: CSP (`django-csp`), Django security settings
- Error reporting: GlitchTip / Sentry via `sentry-sdk`
- CI: GitHub Actions · Deploy: Fly.io

## Local dev

```sh
cp .env.example .env   # edit DJANGO_SECRET_KEY at minimum
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000>

MinIO console: <http://localhost:9001> (minioadmin / minioadmin)

### Adding a dependency

```sh
uv add somepkg
docker compose build web worker
docker compose up -d
```

## Commands

```sh
uv run manage.py runserver       # Django dev server (config.settings.local)
DJANGO_SETTINGS_MODULE=config.settings.bolt uv run manage.py runbolt --dev --port 8001
uv run pytest
uv run ruff check .
uv run pyright
```

## Fly.io deploy

```sh
fly launch --no-deploy
fly postgres create && fly postgres attach <db-name>
fly redis create && fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=<your-app>.fly.dev \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.fly.dev \
    POSTMARK_SERVER_TOKEN=<token> \
    DEFAULT_FROM_EMAIL=no-reply@example.com \
    SERVER_EMAIL=django@example.com \
    AWS_ACCESS_KEY_ID=... \
    AWS_SECRET_ACCESS_KEY=... \
    AWS_STORAGE_BUCKET_NAME=... \
    SENTRY_DSN=...
fly deploy
```

Release command (`fly.toml`): runs `migrate` + `collectstatic` before traffic shifts.

Processes: `web` (gunicorn), `worker` (celery), `bolt` (runbolt on port 8002).

## GDPR commands

```sh
uv run manage.py export_user_data <user_id>   # JSON to stdout
uv run manage.py delete_user <user_id> --confirm
```

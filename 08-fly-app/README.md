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

| Layer | Technology |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 7 |
| Object storage | S3-compatible (MinIO locally, real S3 in prod) |
| Auth | django-mail-auth (passwordless magic-link) |
| Auth hardening | django-axes (brute-force lockout) |
| Tasks | Celery |
| REST API | django-bolt (fast-path, separate process) |
| Email | django-anymail (Postmark in prod, console in dev) |
| Analytics | Google Analytics 4 |
| Error reporting | GlitchTip via sentry-sdk |
| Security | django-csp, Django security headers |
| Deploy | Fly.io (web + worker + bolt processes) |
| CI | GitHub Actions |

## Local development

```sh
cp .env.example .env
# edit .env: set DJANGO_SECRET_KEY to a real random value
docker compose up -d --wait
docker compose exec -T web python manage.py migrate
docker compose exec -T web python manage.py createsuperuser
```

Open <http://localhost:8000/admin/> to log in.

### Task runner (mise)

```sh
mise run dev           # runserver
mise run migrate       # manage.py migrate
mise run makemigrations
mise run test          # pytest
mise run lint          # ruff check
mise run fmt           # ruff format
mise run typecheck     # pyright
mise run worker        # celery worker
mise run bolt          # runbolt on port 8000 (bolt settings)
mise run superuser
```

First-time: `mise trust && mise install`.

Fallback (no mise): `uv run manage.py <cmd>` / `uv run pytest` / `uv run celery ...`.

### Adding a dependency

```sh
uv add somepkg
docker compose build web worker
docker compose up -d
```

### Two HTTP servers in dev

- `python manage.py runserver` — admin, auth, classic Django views (port 8000)
- `DJANGO_SETTINGS_MODULE=config.settings.bolt python manage.py runbolt --dev` — Bolt API on its own port

The Bolt server uses stripped-down settings (no sessions, no templates, no admin) for maximum throughput.

### MinIO (local S3)

MinIO console: <http://localhost:9001> (credentials from `.env`).  
Create a bucket matching `AWS_STORAGE_BUCKET_NAME` and set `AWS_STORAGE_BUCKET_NAME` in `.env` to enable media uploads.

## Health checks

- `GET /healthz` → `ok` (liveness — no external checks)
- `GET /readyz` → `ready` (readiness — DB connection verified)

## GDPR

```sh
python manage.py export_user_data <user_id>   # data portability export
python manage.py delete_user <user_id>        # right to erasure
```

## Deploy (Fly.io)

```sh
fly launch --no-deploy
fly postgres create && fly postgres attach <db-name>
fly redis create && fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=08-fly-app.fly.dev \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://08-fly-app.fly.dev \
    DEFAULT_FROM_EMAIL=no-reply@example.com \
    POSTMARK_SERVER_TOKEN=<token> \
    ANYMAIL_WEBHOOK_SECRET=<secret> \
    AWS_ACCESS_KEY_ID=<key> \
    AWS_SECRET_ACCESS_KEY=<secret> \
    AWS_STORAGE_BUCKET_NAME=<bucket>
mise run deploy    # fly deploy
```

The `[deploy] release_command` in `fly.toml` runs `migrate` + `collectstatic` automatically before each deploy.

Three processes run on Fly:
- **web** — gunicorn serving Django admin and auth views
- **worker** — Celery background task worker
- **bolt** — django-bolt API server (`config.settings.bolt`, port 8002)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

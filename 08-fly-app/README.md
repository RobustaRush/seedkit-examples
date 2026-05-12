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

Production Django app deployed to Fly.io with multi-stage slim runtime image and S3-compatible object storage.

## Stack

| Component | Choice |
|---|---|
| Framework | Django 6 |
| Settings | Split (`base` / `local` / `production` / `test` / `bolt`) |
| Database | PostgreSQL (`psycopg[binary]`) |
| Cache | Redis (`django-redis`) |
| Background tasks | Celery + Redis broker |
| Storage | S3-compatible (`django-storages[s3]`); MinIO in dev |
| Auth | `django-mail-auth` passwordless magic-link |
| Auth hardening | `django-axes` brute-force lockout |
| Email | `django-anymail[postmark]` (console in dev) |
| REST API | `django-bolt` with fast-path settings (`config.settings.bolt`) |
| Analytics | Google Analytics 4 |
| Security | HTTPS headers, HSTS, `django-csp` |
| Error reporting | GlitchTip via `sentry-sdk` |
| GDPR | PII scrubbing in error reports; `export_user_data` / `delete_user_data` commands |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Type check | pyright + django-stubs |
| Task runner | mise |
| Deploy | Fly.io (`fly.toml` with `web` + `worker` + `bolt` processes) |
| CI | GitHub Actions (`test.yml`) |

## Quick start

```sh
cp .env.example .env          # fill in real values
mise trust && mise install    # installs Python 3.12 + uv sync
```

### docker-compose (recommended for local dev)

```sh
docker compose up -d --build --wait
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

MinIO console: <http://localhost:9001> (user/pass from `.env` `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`).

## Task runner commands

| Task | What it does |
|---|---|
| `mise run dev` | `uv run manage.py runserver` |
| `mise run bolt` | Bolt API server on port 8001 (bolt settings) |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run makemigrations` | `uv run manage.py makemigrations` |
| `mise run shell` | Django shell |
| `mise run superuser` | `createsuperuser` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run worker` | Celery worker |
| `mise run deploy` | `fly deploy` |

Raw fallback (without mise): `uv run manage.py <cmd>`.

## Health checks

- `GET /healthz` → `ok` (liveness — no external deps)
- `GET /readyz` → `ready` (readiness — DB probe)

## django-bolt fast-path API

Two servers, two ports:

```sh
# Full Django stack (admin, auth, classic views)
mise run dev                  # port 8000

# Bolt API (stripped settings, high-RPS path)
mise run bolt                 # port 8001
```

Endpoint: `GET /users/{user_id}` → `{"id": ..., "username": "..."}`.

## GDPR management commands

```sh
uv run manage.py export_user_data <user_id>   # JSON dump
uv run manage.py delete_user_data <user_id>   # permanent delete
```

## Env vars

Copy `.env.example` → `.env` and fill in:

| Var | Notes |
|---|---|
| `DJANGO_SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` |
| `REDIS_URL` | `redis://host:6379` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_STORAGE_BUCKET_NAME` | S3 creds |
| `AWS_S3_ENDPOINT_URL` | MinIO endpoint in dev (e.g. `http://minio:9000`) |
| `POSTMARK_SERVER_TOKEN` | Anymail — Postmark API key (prod only) |
| `ANYMAIL_WEBHOOK_SECRET` | Webhook auth secret |
| `ANALYTICS_ID` | GA4 measurement ID (`G-XXXXXXX`) |
| `SENTRY_DSN` | GlitchTip / Sentry DSN (optional) |

## Deploy

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
    AWS_STORAGE_BUCKET_NAME=<bucket>
fly deploy
```

Fly's release command runs `manage.py migrate && collectstatic` before traffic switches over. No manual migration step needed.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

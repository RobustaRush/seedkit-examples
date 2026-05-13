## Prompt

```
/seedkit-slim

Project name: 07-vps-sqlite-saas
Purpose: production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

Settings layout: split.
Database: SQLite.
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: yes.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login + mandatory verification).
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: mise.
Add-ons:
  - cache backend: sqlite (separate `cache.sqlite3` + `CacheRouter` + `DatabaseCache`)
  - tasks: Django Tasks with the Database backend (`django-tasks-db`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - storage: WhiteNoise (static), media volume on the VPS host
  - email: SMTP in production, console backend in local. Use a placeholder Postmark URL (`EMAIL_URL=smtp+tls://<token>:<token>@smtp.postmarkapp.com:587`); also wire `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`, `DJANGO_ADMINS`.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: `django-axes` (yes), 2FA (yes).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings (HSTS, secure cookies, X-Frame, SSL redirect)
  - CSP via `django-csp`: yes
  - error reporting: Sentry SaaS (sentry-sdk)
  - CI: GitHub Actions test workflow
  - deploy target: VPS (Docker + Caddy)
  - database backups: Litestream replication to S3-compatible storage; do not use `django-dbbackup`
  - production Dockerfile: multi-stage with the Litestream `.deb` installed in the prod stage; ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
Skip GDPR for this case.

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `Caddyfile`, `litestream.yml`, `entrypoint.sh`, `.github/workflows/test.yml`. Do not actually push to a remote VPS — just verify all artifacts are present and `docker build .` succeeds.
```

---

# 07-vps-sqlite-saas

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | SQLite (default) + SQLite cache DB |
| Auth | django-allauth (email + mandatory verification) + 2FA (TOTP) |
| Auth hardening | django-axes (lockout after 5 failures) |
| Background tasks | django-tasks-db (DatabaseBackend) |
| Static files | WhiteNoise |
| Logging | structlog (pretty dev / JSON prod, `request_id` per request) |
| Security | django-csp, HSTS, secure cookies, X-Frame DENY |
| Error reporting | Sentry |
| Replication | Litestream → S3-compatible |
| Runtime | Gunicorn (WSGI) |
| Reverse proxy | Caddy (TLS auto) |
| CI | GitHub Actions |

## Local development

```sh
uv sync
uv run manage.py migrate
uv run manage.py createcachetable --database cache
uv run manage.py createsuperuser
uv run manage.py runserver
```

Or with mise:

```sh
mise run migrate
mise run dev
```

## Environment

Copy `.env.production.example` to `.env.production` and fill in the values before deploying.

Key variables:
- `SECRET_KEY` — long random string
- `ALLOWED_HOSTS` — comma-separated hostnames
- `EMAIL_URL` — SMTP URL (Postmark format included as placeholder)
- `SENTRY_DSN` — Sentry project DSN
- `LITESTREAM_*` — S3-compatible credentials and bucket

## Deploy (VPS)

```sh
# Build and push image
docker build --target prod -t your-registry/07-vps-sqlite-saas:latest .
docker push your-registry/07-vps-sqlite-saas:latest

# On the VPS
docker compose -f docker-compose.prod.yml up -d --wait
```

Update `Caddyfile` with your real domain before deploying.

## Tests

```sh
uv run pytest
uv run ruff check .
uv run pyright
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

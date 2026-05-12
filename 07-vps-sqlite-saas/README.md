## Prompt

```
/seedkit

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
  - database backups: Litestream replication to S3-compatible storage (the SQLite production path in `references/database.md`); do not use `django-dbbackup`
  - production Dockerfile: multi-stage (per `references/docker.md`) with the Litestream `.deb` installed in the prod stage; ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
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
| Database | SQLite (WAL + IMMEDIATE) via django-environ |
| Cache | SQLite `cache.sqlite3` via DatabaseCache + CacheRouter |
| Background tasks | django-tasks-db (Database backend) |
| Auth | django-allauth (email-only, mandatory verification in prod) |
| Auth hardening | django-axes (brute-force lockout) + allauth.mfa (TOTP 2FA) |
| User model | Custom `users.User` (email as USERNAME_FIELD, no username) |
| Static files | WhiteNoise (CompressedManifest in prod) |
| Email | Console in dev · SMTP (Postmark) in prod |
| Logging | structlog (pretty in dev, JSON in prod) via django-structlog |
| Replication | Litestream → S3-compatible storage |
| Reverse proxy | Caddy (TLS + media serving) |
| Error reporting | Sentry SDK |
| CSP | django-csp |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Types | pyright + django-stubs |
| Hooks | pre-commit |
| Tasks | mise |

## Setup

```sh
cp .env.example .env
# Set DJANGO_SECRET_KEY in .env

mise run install
mise run migrate
uv run manage.py createcachetable --database cache
mise run superuser
mise run dev
```

## Commands

| Task | Command |
|---|---|
| Install deps | `mise run install` |
| Run dev server | `mise run dev` |
| Migrate | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Shell | `mise run shell` |
| Create superuser | `mise run superuser` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Collect static | `mise run collectstatic` |
| Run task worker | `mise run worker` |

Raw uv fallback: `uv run manage.py <cmd>`.

## Environment variables

See `.env.example` for the full list. Key production variables:

```sh
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com
DATABASE_URL=sqlite:////data/site.sqlite3
CACHE_DB_PATH=/data/cache.sqlite3
EMAIL_URL=smtp+tls://<token>:<token>@smtp.postmarkapp.com:587
DEFAULT_FROM_EMAIL=no-reply@example.com
SERVER_EMAIL=django@example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com
DJANGO_BEHIND_PROXY=True
SENTRY_DSN=...
S3_ENDPOINT=...
S3_BUCKET=...
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
```

## Health checks

- `GET /healthz` → `ok` (liveness — no external deps)
- `GET /readyz` → `ready` (readiness — DB probe)

## Deploy

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d
```

Litestream restores the DB from S3 on first boot, runs migrations, then wraps gunicorn under `litestream replicate`.

Update `deploy/Caddyfile` with your real domain before first deploy.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

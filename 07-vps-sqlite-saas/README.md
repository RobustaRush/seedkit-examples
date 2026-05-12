## Prompt

```
/seedkit

Project name: 07-vps-sqlite-saas
Purpose: production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

Settings layout: split.
Database: SQLite.
Local dev mode: docker-compose (full stack: web only — no db / redis services).
Docker structure: simple (separate `Dockerfile.dev` for dev, single-stage production `Dockerfile`).
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
  - production Dockerfile: single-stage; install the Litestream `.deb`, ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
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
| Database | SQLite (WAL, IMMEDIATE, mmap) |
| Cache | SQLite (`cache.sqlite3`) via `DatabaseCache` |
| Auth | django-allauth (email), django-axes, allauth.mfa (TOTP 2FA) |
| Tasks | django-tasks-db (DB backend) |
| Static files | WhiteNoise |
| Logging | structlog (JSON prod / pretty dev) |
| Error reporting | Sentry SaaS |
| Replication | Litestream → S3-compatible |
| Reverse proxy | Caddy (TLS + media) |
| Task runner | mise |

## Setup

```sh
cp .env.example .env
# edit .env — set DJANGO_SECRET_KEY to a random value

mise run install   # uv sync
mise run migrate
mise run superuser
mise run dev       # http://127.0.0.1:8000
```

Or with Docker (local dev):

```sh
cp .env.example .env
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createcachetable --database cache
# http://localhost:8000
```

## Tasks

| Task | Command |
|---|---|
| `mise run dev` | `uv run manage.py runserver` |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run worker` | `uv run manage.py db_worker` |
| `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |

## Deploy (VPS)

On the VPS, create `/srv/07-vps-sqlite-saas/.env.prod` with real values, then:

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d
```

Litestream restores the SQLite DB from S3 on boot (if the volume is empty), runs migrations, then starts `gunicorn` under `litestream replicate`.

Edit `deploy/Caddyfile` to replace `example.com` with your real domain before first deploy.

## Pre-commit

```sh
uv run pre-commit install
```

Hooks: trailing whitespace, YAML check, Ruff lint+format, pyright.

> NB: TOTP 2FA requires accurate server time (NTP). Clock skew > 30s causes auth failures.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

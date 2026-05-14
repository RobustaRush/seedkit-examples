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
| Database | SQLite (WAL + IMMEDIATE, `/data/site.sqlite3` on a persistent volume) |
| Cache | SQLite (`/data/cache.sqlite3` via `CacheRouter`) |
| Task queue | Django Tasks + `django-tasks-db` database backend |
| Auth | `django-allauth` (email login, mandatory verification in prod) |
| 2FA | `allauth.mfa` (TOTP + recovery codes) |
| Brute-force | `django-axes` |
| Static files | WhiteNoise (compressed manifest in prod) |
| Media | Docker named volume, served by Caddy |
| Logging | `structlog` — pretty console in dev, JSON in prod |
| Server | Gunicorn under `litestream replicate` |
| Reverse proxy | Caddy (TLS, media, health probe) |
| DB backup | Litestream streaming replication to S3-compatible storage |
| Error tracking | Sentry SaaS (`SENTRY_DSN` env var) |
| CI | GitHub Actions (`pytest`, `ruff`, `pyright`) |

## Local setup

```sh
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY and DJANGO_DEBUG=True

mise install           # or: uv sync
mise run migrate
mise run dev           # http://localhost:8000
```

Or without mise:

```sh
uv sync
uv run manage.py migrate
uv run manage.py createcachetable --database cache
uv run manage.py runserver
```

## Common tasks

| Task | Command |
|---|---|
| Run dev server | `mise run dev` |
| Run migrations | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Open Django shell | `mise run shell` |
| Create superuser | `mise run superuser` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Collect static | `mise run collectstatic` |
| Run task worker | `mise run worker` |

## Health endpoints

- `GET /healthz` — liveness (always fast, no DB check)
- `GET /readyz` — readiness (checks DB connectivity)

## Deploy

Copy `.env.example` to `.env.prod` on the VPS and fill in all values. Then:

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d
```

Migrations and `createcachetable` run automatically inside `entrypoint.sh` on container start (after Litestream restores the DB from S3).

### Caddyfile

Edit `deploy/Caddyfile` — replace `example.com` with your real domain.

### Litestream

Set the S3 vars in `.env.prod`:

```sh
S3_ENDPOINT=https://s3.example.com
S3_BUCKET=my-bucket
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
DATABASE_URL=sqlite:////data/site.sqlite3
CACHE_DB_PATH=/data/cache.sqlite3
DJANGO_BEHIND_PROXY=True
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com
```

## Background tasks

Add tasks to `jobs/tasks.py`:

```python
from django.tasks import task

@task()
def my_task(arg: str) -> None:
    ...
```

Enqueue from anywhere:

```python
from jobs.tasks import my_task
my_task.enqueue("hello")
```

Run the worker:

```sh
mise run worker     # uv run manage.py db_worker
```

## Pre-commit hooks

```sh
uv run pre-commit install
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

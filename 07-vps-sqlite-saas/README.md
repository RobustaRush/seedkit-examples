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
| Framework | Django 6.x |
| Database | SQLite (WAL mode) + Litestream → S3 replication |
| Cache | SQLite (`cache.sqlite3`) via `DatabaseCache` |
| Background tasks | `django-tasks-db` (no broker) |
| Auth | `django-allauth` (email-only) + `django-axes` lockout + TOTP 2FA |
| Static files | WhiteNoise (`CompressedManifestStaticFilesStorage` in prod) |
| Logging | `structlog` — JSON in prod, pretty-console in dev |
| Server | Gunicorn (WSGI), wrapped by Litestream in prod |
| Reverse proxy | Caddy (TLS, media serving) |
| Error reporting | Sentry |
| CSP | `django-csp` |
| Lint | Ruff |
| Types | Pyright + django-stubs |
| Tests | pytest + pytest-django |
| CI | GitHub Actions |
| Task runner | mise |

## Local development

```sh
cp .env.example .env          # generate a real key: see .env.example
docker compose up -d --wait   # builds Dockerfile.dev, mounts source
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createcachetable --database cache
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

## mise tasks

```sh
mise run migrate       # uv run manage.py migrate
mise run test          # uv run pytest
mise run lint          # uv run ruff check .
mise run fmt           # uv run ruff format .
mise run typecheck     # uv run pyright
mise run worker        # uv run manage.py db_worker
mise run superuser     # uv run manage.py createsuperuser
```

Without mise: `uv run manage.py <cmd>`.

## Pre-commit hooks

```sh
uv run pre-commit install
```

Hooks: trailing-whitespace, end-of-file-fixer, check-yaml, ruff, ruff-format, pyright.

## Production environment variables

Copy `.env.example` to `.env.prod` on the VPS and fill in all values:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Long random string |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `example.com` |
| `DATABASE_URL` | `sqlite:////data/site.sqlite3` |
| `CACHE_DB_PATH` | `/data/cache.sqlite3` |
| `EMAIL_URL` | `smtp+tls://<token>:<token>@smtp.postmarkapp.com:587` |
| `DEFAULT_FROM_EMAIL` | `no-reply@example.com` |
| `SERVER_EMAIL` | `django@example.com` |
| `DJANGO_ADMINS` | `ops@example.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://example.com` |
| `DJANGO_BEHIND_PROXY` | `True` |
| `DJANGO_SITE_DOMAIN` | `example.com` (TOTP issuer name) |
| `SENTRY_DSN` | Sentry project DSN |
| `S3_ENDPOINT` | Litestream S3-compatible endpoint |
| `S3_BUCKET` | Litestream bucket name |
| `S3_ACCESS_KEY_ID` | Litestream credentials |
| `S3_SECRET_ACCESS_KEY` | Litestream credentials |

## Deploy

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d
```

The `entrypoint.sh` restores the SQLite DB from Litestream on first boot, runs `migrate`, creates the cache table, then execs `litestream replicate -exec "gunicorn ..."`.

Update `deploy/Caddyfile` with your real domain before first deploy.

## Background tasks

Add `@task`-decorated functions to `jobs/tasks.py`. Enqueue from anywhere:

```python
from jobs.tasks import example_task
example_task.enqueue("hello")
```

Run the worker: `mise run worker` (or `uv run manage.py db_worker`).

## Health checks

- `GET /healthz` → `ok` (liveness — no DB check)
- `GET /readyz` → `ready` (readiness — DB SELECT 1)

Caddy probes `/healthz` via `health_uri`. Monitoring should watch `/readyz`.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

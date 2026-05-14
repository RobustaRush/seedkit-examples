## Prompt

```
/seedkit-slim

Project name: 09-ssh-deploy
Purpose: production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

Settings layout: split.
Database: PostgreSQL.
Postgres location: Postgres-in-Docker (`db` + `redis` services in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: mise.
Add-ons:
  - redis
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - analytics: Umami (self-hosted, env-driven website ID and host)
  - email: none (this project does not send transactional mail and the test verifies the skip path).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings
  - CSP via `django-csp`: yes
  - error reporting: Bugsink (self-hosted, sentry-sdk DSN)
  - GDPR: PII scrubbing in error reports, retention defaults, user data export/delete
  - CI: GitHub Actions test workflow
  - deploy: GitHub Actions deploy via SSH (rsync + remote `docker compose pull && up -d`)
  - database backups via `django-dbbackup`: yes (self-managed host — no native backup service)
  - production Dockerfile: multi-stage — uv builder → `python:3.12-slim-bookworm` runtime

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6 |
| Database | PostgreSQL 16 (Docker, host port 5433) |
| Cache / Queue | Redis 7 (Docker) |
| Background tasks | django-tasks-rq + RQ |
| Logging | structlog — pretty dev / JSON prod |
| Error reporting | Bugsink / sentry-sdk |
| CSP | django-csp 4.0 |
| DB backups | django-dbbackup |
| Analytics | Umami (self-hosted, env-driven) |
| WSGI server | Gunicorn |
| Linting | Ruff |
| Tests | pytest + pytest-django |
| Task runner | mise |
| CI | GitHub Actions (test.yml) |
| Deploy | GitHub Actions → SSH → rsync + docker compose (deploy.yml) |

## Local setup

```sh
cp .env.example .env          # edit SECRET_KEY at minimum
docker compose up -d --wait   # starts postgres:5433 + redis:6379
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Worker (separate terminal):

```sh
uv run manage.py rqworker default
```

## Key URLs

| URL | Purpose |
|---|---|
| `/admin/` | Django admin |
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe (hits DB) |
| `/django-rq/` | RQ dashboard (admin-protected) |

## mise tasks

```sh
mise run server          # runserver
mise run worker          # rqworker default
mise run migrate
mise run test
mise run lint
mise run dbbackup
```

## Deploy

Requires three GitHub Actions secrets:

- `SSH_HOST` — remote server IP / hostname
- `SSH_USER` — SSH login user
- `SSH_KEY` — private key with access to the host

The deploy workflow:
1. Syncs code via `rsync`
2. Builds the image on the remote host (`docker build --target prod`)
3. Runs `docker compose -f docker-compose.prod.yml up -d` + `migrate`

Copy `.env.example` to `.env.prod` on the remote host and fill in real values before first deploy.

## GDPR commands

```sh
uv run manage.py gdpr_export <user_id>          # JSON export (Art. 20)
uv run manage.py gdpr_delete <user_id> --confirm  # anonymise (Art. 17)
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

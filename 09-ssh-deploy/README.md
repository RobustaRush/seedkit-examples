## Prompt

```
/seedkit

Project name: 09-ssh-deploy
Purpose: production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

Settings layout: split.
Database: PostgreSQL.
Local dev mode: docker-compose (web + db + redis).
Docker structure: override (one multi-stage `Dockerfile` with `dev`/`prod` targets, `docker-compose.yml` + `docker-compose.override.yml`).
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
  - email: none (deliberately skip `references/email.md`; this project does not send transactional mail and the test verifies the skip path).
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
  - production Dockerfile: single-stage (small enough; multi-stage not needed)

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 7 |
| Background tasks | Django Tasks + django-tasks-rq |
| Logging | structlog (JSON in prod, pretty in dev) |
| Analytics | Umami (self-hosted) |
| Error reporting | Bugsink (self-hosted, sentry-sdk DSN) |
| Backups | django-dbbackup → S3-compatible storage |
| Server | gunicorn |
| Deploy | GitHub Actions → SSH rsync + docker compose |

## Quick start

```sh
# First time
cp .env.example .env           # then set DJANGO_SECRET_KEY
mise run install               # uv sync

# Local dev (docker-compose)
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
# → http://localhost:8000/admin/
```

## Task runner (mise)

```sh
mise run dev            # uv run manage.py runserver
mise run migrate        # uv run manage.py migrate
mise run test           # uv run pytest
mise run lint           # uv run ruff check .
mise run fmt            # uv run ruff format .
mise run worker         # uv run manage.py rqworker default
mise run superuser      # uv run manage.py createsuperuser
```

Without mise: `uv run manage.py <cmd>` / `uv run pytest` / `uv run ruff check .`

## Health checks

- `GET /healthz` → `ok` (liveness — process is alive)
- `GET /readyz` → `ready` (readiness — DB reachable)

## Background tasks

Add `@task`-decorated functions to `jobs/tasks.py`. They are registered via `JobsConfig.ready()` and enqueued with `sample_task.enqueue("arg")`. The worker runs `manage.py rqworker default`.

## GDPR

```sh
uv run manage.py export_user_data <user_id>   # Article 20 export
uv run manage.py delete_user_data <user_id>   # Article 17 erasure
```

## Database backups

Configured in `production.py` via `django-dbbackup` → S3-compatible bucket. Run from a cron job on the host:

```sh
docker compose exec -T web python manage.py dbbackup --clean
```

## Deploy

```sh
# One-time on the server:
mkdir -p /srv/09-ssh-deploy/deploy
scp deploy/.env.prod.example user@host:/srv/09-ssh-deploy/deploy/.env.prod
# Fill in /srv/09-ssh-deploy/deploy/.env.prod

# CI deploys automatically on push to main.
# Manual:
mise run deploy
```

Requires GitHub repo secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN`.

## Environment variables

See `.env.example` (dev) and `deploy/.env.prod.example` (production) for the full list.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

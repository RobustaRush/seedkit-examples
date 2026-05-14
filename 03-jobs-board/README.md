## Prompt

```
/seedkit-slim

Project name: 03-jobs-board
Purpose: job board with background email notifications and a daily digest.

Settings layout: single file.
Database: PostgreSQL.
Postgres location: Postgres in Docker (`docker-compose.yml`, port `127.0.0.1:5432` published to the host).
Lint with Ruff: no.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): yes.
Custom user model: no.
Auth add-on: `django-mail-auth` (passwordless magic-link).
Structured logging: no.
Task runner: just.
Add-ons:
  - redis (for Celery)
  - tasks: Celery, with periodic tasks (Celery Beat). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, and add a sample `@shared_task` to `jobs/tasks.py` referenced from `CELERY_BEAT_SCHEDULE`.
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.

Production setup: skip.

Ship a `docker-compose.yml` with `db` and `redis` services only. Run the foundation, start the containers, run migrate + createsuperuser, and define one trivial Celery task plus one Beat-scheduled task to prove autodiscovery works.
```

---

# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 16 (Docker) |
| Auth | django-mail-auth (passwordless magic-link) |
| Background tasks | Celery + Celery Beat |
| Message broker | Redis 7 (Docker) |
| Email (dev) | Console backend |
| i18n | Django gettext |
| Task runner | just |

## Quick start

```sh
# 1. Start services
docker compose up -d --wait

# 2. Apply migrations
just migrate

# 3. Create admin user
just superuser

# 4. Run server
just serve

# 5. (optional) Run Celery worker + beat in separate terminals
just worker
just beat
```

## Key URLs

- `/admin/` — Django admin
- `/accounts/login/` — magic-link login
- `/healthz` — liveness probe
- `/readyz` — readiness probe (hits DB)

## Environment variables

Copy `.env.example` to `.env` and adjust as needed.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

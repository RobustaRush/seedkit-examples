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

| Component | Choice |
|-----------|--------|
| Framework | Django 5.x |
| Database | PostgreSQL 17 (Docker) |
| Task queue | Celery + Redis |
| Periodic tasks | Celery Beat (DB scheduler) |
| Auth | django-mail-auth (passwordless magic-link) |
| Email (local) | Console backend |
| i18n | Django gettext + LocaleMiddleware |
| Task runner | just |

## Quick start

```bash
# Start services
just up

# Apply migrations
just migrate

# Create admin user
just createsuperuser

# Run dev server
just run

# Run Celery worker (separate terminal)
just worker

# Run Celery Beat (separate terminal)
just beat
```

## Key URLs

- Admin: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/accounts/login/
- Health: http://127.0.0.1:8000/healthz
- Ready: http://127.0.0.1:8000/readyz

## Celery tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| `jobs.tasks.send_daily_digest` | Daily 08:00 UTC | Digest of active job posts |
| `jobs.tasks.notify_new_job` | On demand | Notify subscribers of new post |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

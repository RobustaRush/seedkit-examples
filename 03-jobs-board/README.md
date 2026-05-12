## Prompt

```
/seedkit

Project name: 03-jobs-board
Purpose: job board with background email notifications and a daily digest.

Settings layout: single file.
Database: PostgreSQL.
Postgres location: Postgres in Docker (`docker-compose.yml` from `references/docker.md`, port `127.0.0.1:5432` published to the host).
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

- Django 6 · PostgreSQL · django-environ
- Auth: django-mail-auth (passwordless magic-link)
- Background tasks: Celery + Redis + Celery Beat
- Health checks: `/healthz` (liveness) · `/readyz` (readiness)
- i18n: gettext + LocaleMiddleware
- Task runner: just

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)
- Docker (for Postgres + Redis)

## Setup

```sh
cp .env.example .env          # then edit DJANGO_SECRET_KEY
docker compose up -d --wait   # start Postgres + Redis
just migrate
just superuser
just dev
```

Open <http://127.0.0.1:8000/admin/> to sign in.

## Tasks

| Task | Description |
|------|-------------|
| `just install` | Install dependencies |
| `just dev` | Start development server |
| `just migrate` | Run database migrations |
| `just makemigrations` | Create new migrations |
| `just shell` | Open Django shell |
| `just superuser` | Create superuser |
| `just test` | Run test suite |
| `just worker` | Start Celery worker |
| `just beat` | Start Celery Beat scheduler |

Or use `uv run manage.py <cmd>` directly.

## Celery tasks

- `jobs.tasks.send_notification_email(job_id, recipient_email)` — ad-hoc notification
- `jobs.tasks.send_daily_digest()` — scheduled daily at 08:00 via `CELERY_BEAT_SCHEDULE`

## Health checks

- `GET /healthz` → `ok` (liveness)
- `GET /readyz` → `ready` (readiness — checks DB)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

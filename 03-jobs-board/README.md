## Prompt

```
/seedkit

Project name: 03-jobs-board
Purpose: job board with background email notifications and a daily digest.

Settings layout: single file.
Database: PostgreSQL.
Local dev mode: uv on host. Postgres location: run only Postgres in Docker, Django runs on the host (publish 5432 to localhost).
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

- Django 6 · PostgreSQL · Celery + Beat · Redis
- Auth: `django-mail-auth` (passwordless magic-link)
- Health checks: `/healthz`, `/readyz`
- i18n: gettext / LocaleMiddleware
- Task runner: just

## Setup

```sh
cp .env.example .env   # edit DJANGO_SECRET_KEY
just install
docker compose up -d --wait
just migrate
just superuser
just dev
```

Open <http://localhost:8000/admin/>.

## Tasks

| Task | Command |
|------|---------|
| `just install` | `uv sync` |
| `just dev` | `uv run manage.py runserver` |
| `just migrate` | `uv run manage.py migrate` |
| `just makemigrations` | `uv run manage.py makemigrations` |
| `just shell` | `uv run manage.py shell` |
| `just superuser` | `uv run manage.py createsuperuser` |
| `just test` | `uv run manage.py test` |
| `just worker` | `uv run celery -A config worker -l info` |
| `just beat` | `uv run celery -A config beat -l info` |

## Environment variables

See `.env.example` for all supported env vars.

## Services

The `docker-compose.yml` runs `db` (PostgreSQL 17) and `redis` (Redis 7) only.
Django runs on the host with `just dev`.

## Celery

Autodiscovery scans all `INSTALLED_APPS`. Add `@shared_task` functions to any app's `tasks.py`.

`CELERY_BEAT_SCHEDULE` in `config/settings.py` schedules `jobs.tasks.send_daily_digest` daily at 08:00.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

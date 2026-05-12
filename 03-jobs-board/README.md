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

- Django 6 + django-environ
- PostgreSQL (Docker) · Django runs on the host via uv
- Redis (Docker) · Celery broker + result backend + cache
- Celery + Celery Beat (periodic tasks)
- django-mail-auth (passwordless magic-link)
- i18n (gettext, LocaleMiddleware)
- Health check endpoints (`/healthz`, `/readyz`)

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)
- Docker Desktop (for db + redis)

## Setup

```sh
cp .env.example .env   # edit DJANGO_SECRET_KEY
docker compose up -d --wait
just migrate
just superuser
just dev
```

Open <http://127.0.0.1:8000/admin/> and sign in.

## Commands

| Command | Action |
|---|---|
| `just install` | Install / sync dependencies |
| `just dev` | Start dev server |
| `just migrate` | Run migrations |
| `just makemigrations` | Create migrations |
| `just shell` | Django shell |
| `just superuser` | Create superuser |
| `just test` | Run tests |
| `just worker` | Start Celery worker |
| `just beat` | Start Celery Beat scheduler |

Fallback (no just): `uv run manage.py <cmd>`

## Background tasks

Tasks live in `jobs/tasks.py`. The Beat schedule is in `CELERY_BEAT_SCHEDULE` in `config/settings.py`. Run worker and beat in separate terminals for local development.

## Auth

Magic-link login — users enter their email and receive a one-time sign-in link. The link prints to `runserver` stdout when `EMAIL_URL=consolemail://`.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

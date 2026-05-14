## Prompt

```
/seedkit

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

- **Django 6** + **PostgreSQL** (Docker) + **Redis** (Docker)
- **django-mail-auth** — passwordless magic-link authentication
- **Celery** + **Celery Beat** — background tasks and periodic digest
- **django-redis** — shared Redis cache
- **i18n** — gettext / LocaleMiddleware
- Health checks at `/healthz` and `/readyz`

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)
- Docker

## Setup

```sh
cp .env.example .env           # edit DJANGO_SECRET_KEY
docker compose up -d --wait    # start Postgres + Redis
just migrate
just superuser
just dev
```

Open <http://127.0.0.1:8000/admin/> and sign in with the superuser credentials.

## Key commands

| Task | Command |
|---|---|
| Install deps | `just install` |
| Run dev server | `just dev` |
| Apply migrations | `just migrate` |
| Make migrations | `just makemigrations` |
| Django shell | `just shell` |
| Create superuser | `just superuser` |
| Run tests | `just test` |
| Celery worker | `just worker` |
| Celery Beat | `just beat` |

Fallback (no `just`): `uv run manage.py <command>`

## Background tasks

- `jobs.tasks.send_daily_digest` — triggered daily at 08:00 via Beat, sends the job digest to subscribers.
- Run `just worker` and `just beat` alongside `just dev` for local testing.

## i18n

```sh
uv run manage.py makemessages -l de   # add a language
uv run manage.py compilemessages
```

Commit `.po` files; `.mo` files are compiled at deploy time.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

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
  - tasks: Celery, with periodic tasks (Celery Beat)
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

**Stack:** Django 6 · PostgreSQL · Redis · Celery + Beat · django-mail-auth · i18n

## Quick start

```sh
cp .env.example .env          # edit DJANGO_SECRET_KEY
docker compose up -d --wait   # starts db + redis
just migrate
just superuser
just dev                      # http://127.0.0.1:8000
```

## Tasks

| Command | Description |
|---|---|
| `just install` | `uv sync` |
| `just dev` | Django dev server |
| `just migrate` | Run migrations |
| `just makemigrations` | Create new migrations |
| `just shell` | Django shell |
| `just superuser` | Create superuser |
| `just test` | Run tests |
| `just worker` | Celery worker |
| `just beat` | Celery Beat scheduler |
| `just collectstatic` | Collect static files |

Fallback (no `just`): `uv run manage.py <cmd>`

## Auth

Passwordless magic-link via `django-mail-auth`. With `EMAIL_URL=consolemail://` the sign-in link prints to `runserver` stdout — click it to log in.

## Background tasks

`jobs/tasks.py` defines two tasks:

- `send_application_notification` — triggered on application submission
- `daily_digest` — scheduled daily at 08:00 via Celery Beat

Run worker and Beat locally:

```sh
just worker   # in one terminal
just beat     # in another
```

## i18n

```sh
uv run manage.py makemessages -l de
# edit locale/de/LC_MESSAGES/django.po
uv run manage.py compilemessages
```

## Health checks

- `GET /healthz` → `ok` (liveness)
- `GET /readyz` → `ready` (readiness — checks DB)

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

- **Django** (single-file settings, PostgreSQL, i18n)
- **Auth** — `django-mail-auth` passwordless magic-link (`mailauth.contrib.user`)
- **Cache** — Redis via `django-redis`
- **Background tasks** — Celery + Celery Beat (daily digest at 08:00 UTC)
- **Email** — console backend in dev; set `EMAIL_URL` for production
- **Health checks** — `/healthz` (liveness) and `/readyz` (readiness + DB)
- **Task runner** — `just`

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just)
- Docker (for Postgres + Redis)

## Quick start

```sh
cp .env.example .env        # fill in DJANGO_SECRET_KEY
docker compose up -d --wait # start Postgres + Redis
just migrate
just superuser
just dev
```

Open <http://localhost:8000/admin/>.

## Commands

| Command | Action |
|---|---|
| `just install` | `uv sync` |
| `just dev` | Run dev server |
| `just migrate` | Apply migrations |
| `just makemigrations` | Create new migrations |
| `just shell` | Django shell |
| `just superuser` | Create superuser |
| `just test` | Run test suite |
| `just worker` | Start Celery worker |
| `just beat` | Start Celery Beat scheduler |

## Environment variables

See `.env.example` for all variables. Key ones:

| Variable | Default (dev) | Required in prod |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | yes |
| `DJANGO_DEBUG` | `True` | set to `False` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | yes |
| `DATABASE_URL` | `postgres://postgres:postgres@localhost:5432/postgres` | yes |
| `REDIS_URL` | `redis://127.0.0.1:6379` | yes |
| `EMAIL_URL` | `consolemail://` | yes (real SMTP) |
| `DEFAULT_FROM_EMAIL` | `webmaster@localhost` | yes |

## Celery

The `jobs` app contains the Celery tasks. `CELERY_BEAT_SCHEDULE` in `settings.py`
registers `jobs.tasks.send_daily_digest` to run daily at 08:00 UTC.

Add new tasks by creating `@shared_task` functions in any registered app's `tasks.py`.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

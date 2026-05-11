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

- **Django 6** · single `config/settings.py` · PostgreSQL · uv on host
- **Auth** · `django-mail-auth` (passwordless magic-link)
- **Background tasks** · Celery + Redis · Celery Beat (daily digest)
- **Cache** · `django-redis`
- **i18n** · Django `gettext`, `LocaleMiddleware`
- **Health checks** · `/healthz` · `/readyz`
- **Task runner** · `just`

## Setup

```sh
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY to a real random value
just install
docker compose up -d --wait   # starts Postgres and Redis
just migrate
just superuser
just dev
```

Open <http://127.0.0.1:8000/admin/>.

## Key commands

| Command | Action |
|---|---|
| `just dev` | Start Django dev server |
| `just migrate` | Run migrations |
| `just makemigrations` | Create new migrations |
| `just superuser` | Create superuser |
| `just test` | Run test suite |
| `just worker` | Start Celery worker |
| `just beat` | Start Celery Beat scheduler |
| `just makemessages` | Extract translatable strings |
| `just compilemessages` | Compile `.po` → `.mo` |

## Auth

`django-mail-auth` replaces passwords with one-time magic links. Visit `/accounts/login/`, enter an email, and click the link printed to the console (dev) or delivered by your SMTP provider (prod).

`AUTH_USER_MODEL` is `mailauth_user.EmailUser` — an email-only user with no password column.

## Background tasks

`CELERY_BEAT_SCHEDULE` wires `jobs.tasks.send_daily_digest` to run daily at 08:00 UTC. Add `@shared_task` functions to `jobs/tasks.py`; Celery autodiscovers them via `INSTALLED_APPS`.

```sh
# Run worker and beat in separate terminals
just worker
just beat
```

## Environment variables

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required in prod) |
| `DJANGO_DEBUG` | `True` in dev, unset in prod |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `DATABASE_URL` | Postgres connection URL |
| `REDIS_URL` | Redis base URL (no trailing slash or DB number) |
| `EMAIL_URL` | Email backend URL (`consolemail://` in dev) |
| `DEFAULT_FROM_EMAIL` | From address for outgoing mail |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

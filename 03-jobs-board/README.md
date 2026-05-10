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

## Stack

- Django 6.x (single `config/settings.py`)
- PostgreSQL (Docker) + psycopg
- Redis (Docker) — cache, Celery broker/results
- Celery + Celery Beat (periodic tasks)
- django-mail-auth (passwordless magic-link login)
- i18n enabled (LocaleMiddleware)
- Health check endpoints (`/healthz`, `/readyz`)

## Local dev setup

### Start infrastructure

```sh
docker compose up -d db redis
```

Postgres publishes on `localhost:5432`, Redis on `localhost:6379`.

### Install Python deps

```sh
uv sync
```

### Configure environment

```sh
cp .env.example .env
# .env already has a generated DJANGO_SECRET_KEY if you ran the seed script
```

### Migrate and create superuser

```sh
uv run manage.py migrate
uv run manage.py createsuperuser
```

### Run Django

```sh
uv run manage.py runserver
```

Open <http://localhost:8000/admin/>.

### Run Celery worker

```sh
uv run celery -A config worker -l info
```

### Run Celery Beat (periodic tasks)

```sh
uv run celery -A config beat -l info
```

### Enqueue a task from the shell

```python
# uv run manage.py shell
from jobs.tasks import send_notification_email
send_notification_email.delay(1)   # user pk=1
```

## Beat schedule

| Task | Schedule |
|---|---|
| `jobs.tasks.daily_digest` | Daily at 08:00 UTC |

## Health checks

- `GET /healthz` — liveness (always 200)
- `GET /readyz` — readiness (200 if DB reachable, 503 otherwise)

## Auth

Magic-link login at `/accounts/login/`. Enter your email; click the link printed to the console (dev) or sent via SMTP (production).

# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack

- Django 6 + django-environ (single `config/settings.py`)
- PostgreSQL via psycopg3 (runs in Docker; Django on host)
- Redis 7 (runs in Docker; broker and cache)
- Celery 5 + Beat (periodic tasks)
- django-mail-auth (passwordless magic-link login)
- i18n (gettext, LocaleMiddleware)
- Health check endpoints (`/healthz`, `/readyz`)

## Requirements

- Python 3.12+
- uv
- Docker + Docker Compose

## Setup

```sh
cp .env.example .env
# edit .env and set DJANGO_SECRET_KEY to a real value
docker compose up -d db redis
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
uv run manage.py runserver
uv run celery -A config worker -l info
uv run celery -A config beat -l info
```

## Test

```sh
uv run manage.py test
```

## Enqueue a task from the shell

```python
from jobs.tasks import send_welcome_email
send_welcome_email.delay(1)
```

## Key URLs

- `/admin/` — Django admin (magic-link login)
- `/accounts/login/` — email-only sign-in form
- `/healthz` — liveness probe
- `/readyz` — readiness probe (checks DB)

# 06-silk-lab

Profile request paths with django-silk and run background email tasks on the DB backend.

## Stack

- **Django 6.0** + split settings (base / local / production / test)
- **PostgreSQL** via psycopg + django-environ
- **django-silk** — profiling dashboard + `@silk_profile` (dev only)
- **django-tasks** + **django-tasks-db** — background tasks, DB backend
- **GoatCounter** — self-hosted analytics snippet (env-driven, no-op when `ANALYTICS_ID` is empty)
- **django-zeal** — N+1 detection (dev only)
- **django-migration-linter** — migration safety audits (dev only)
- **django-test-migrations** — migration rollback tests (dev only)
- **django-extensions** — `shell_plus`, `show_urls`, etc. (dev only)
- **Ruff** — linting + formatting

## Setup

```sh
createdb silk_db
cp .env.example .env
# Edit .env and set DATABASE_URL if needed
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Web server
uv run manage.py runserver

# Background worker (separate terminal)
uv run manage.py db_worker
```

## Key URLs

- `/admin/` — Django admin
- `/silk/` — profiling dashboard (DEBUG only)
- `/healthz` — liveness probe
- `/readyz` — readiness probe (checks DB)

## Enqueue a task

```sh
uv run manage.py shell -c "
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue(1)
"
```

## Dev tools

```sh
uv run ruff check .           # lint
uv run ruff format .          # format
uv run manage.py show_urls    # list URL patterns
uv run manage.py lintmigrations  # audit migrations
uv run pytest                 # run tests
```

## GoatCounter analytics

Set in `.env`:

```sh
ANALYTICS_ID=mysite
ANALYTICS_HOST=https://mysite.goatcounter.com
```

Leave empty to disable (snippet is suppressed when `ANALYTICS_ID` is empty or `DEBUG=True`).

## Prompt

```
/seedkit

Project name: 06-silk-lab
Purpose: profile a few request paths with django-silk and run a simple background email task on the DB backend.

Settings layout: split.
Database: PostgreSQL.
Local dev mode: uv on host. Postgres location: on the host (use `createdb silk_db`).
Lint with Ruff: yes.
Test runner: pytest (required for django-test-migrations).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: no.
Add-ons:
  - debug: django-silk (profiling + `@silk_profile`)
  - tasks: Django Tasks with the Database backend (`django-tasks-db`)
  - analytics: GoatCounter (self-hosted snippet, env-driven site code)
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Devcontainer: no.
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: yes.
  - Database safety tools: all three —
      - django-zeal: yes
      - django-migration-linter: yes
      - django-test-migrations: yes

Production setup: skip.

Run the foundation, the boot check, start `manage.py db_worker` in a second terminal, enqueue one example task and confirm it runs. Hit a profiled view and confirm the request appears under `/silk/`. Run `uv run manage.py lintmigrations`. Write a migration test in `jobs/tests/test_migrations.py` using the `migrator` fixture that applies the initial jobs migration forward and rolls it back. Run `uv run pytest`.
```

---

# 06-silk-lab

Profile request paths with django-silk and run background email tasks via Django Tasks (Database backend).

## Stack

- Django 6.0 + django-environ (split settings)
- PostgreSQL (host)
- django-silk — profiling dashboard at `/silk/`
- django-tasks + django-tasks-db — background tasks, no broker required
- GoatCounter — self-hosted analytics snippet (env-driven)
- Email — console backend in dev
- Health checks — `/healthz` (liveness) + `/readyz` (readiness)

### Dev dependencies

- django-silk, django-extensions, django-zeal, django-migration-linter, django-test-migrations
- pytest, pytest-django, ruff

## Setup

```sh
createdb silk_db
cp .env.example .env
# edit .env: set DJANGO_SECRET_KEY
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
uv run manage.py runserver          # web server
uv run manage.py db_worker          # task worker (separate terminal)
```

## Enqueue a task (example)

```python
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue("user@example.com")
```

## Commands

```sh
uv run manage.py show_urls          # list all URL patterns (django-extensions)
uv run manage.py lintmigrations     # audit migrations for unsafe operations
uv run pytest                       # run test suite
uv run ruff check .                 # lint
uv run ruff format .                # format
```

## Health checks

```sh
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

## Silk profiling

Visit `http://localhost:8000/silk/` after making any requests. The `/healthz` view is decorated with `@silk_profile` as a demo.

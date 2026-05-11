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
Task runner: none.
Add-ons:
  - debug: django-silk (profiling + `@silk_profile`)
  - tasks: Django Tasks with the Database backend (`django-tasks-db`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
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

Run the foundation, the boot check, start `manage.py db_worker` in a second terminal, enqueue one example task and confirm it runs. Hit a profiled view and confirm the request appears under `/silk/`. Run `uv run manage.py lintmigrations`. Run `uv run pytest` to confirm the test runner is wired (no project-specific tests required — `django-test-migrations` is installed for the user to write migration tests later).
```

---

# 06-silk-lab

Profile request paths with django-silk and run background tasks on the DB backend.

## Stack

| Layer | Package |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL (`psycopg[binary]`) |
| Settings | Split (`base` / `local` / `production` / `test`) |
| Profiling | django-silk — dashboard at `/silk/`, `@silk_profile` decorator |
| Background tasks | django-tasks-db (`db_worker`) |
| Email (dev) | Console backend |
| Analytics | GoatCounter (env-driven, disabled in dev) |
| Health checks | `/healthz` (liveness), `/readyz` (DB ping) |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Dev extras | django-extensions, django-zeal, django-migration-linter, django-test-migrations |

## Setup

```sh
createdb silk_db
cp .env.example .env   # set DJANGO_SECRET_KEY to a real value
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Web server
uv run manage.py runserver

# Task worker (separate terminal)
uv run manage.py db_worker
```

## Enqueue an example task

```sh
uv run manage.py shell_plus
# In the shell:
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue("you@example.com")
```

## Profiling with Silk

Visit `http://localhost:8000/silk/` after making some requests. Silk records every request automatically.

To profile a specific code block, use the context manager inside a task:

```python
from silk.profiling.profiler import silk_profile

with silk_profile(name="my operation"):
    ...
```

Clear accumulated data when the table grows large:

```sh
uv run manage.py silk_clear_request_log
```

## Lint

```sh
uv run ruff check .
uv run ruff format --check .
```

## Test

```sh
uv run pytest
```

## Migration safety

```sh
uv run manage.py lintmigrations
```

## GoatCounter analytics

Set env vars to enable (empty `ANALYTICS_ID` disables tracking — safe in dev):

```sh
ANALYTICS_HOST=https://stats.example.com
ANALYTICS_ID=mysite
```

Include `{% include "_analytics.html" %}` before `</body>` in your base template.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

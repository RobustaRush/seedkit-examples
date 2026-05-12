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

Profile a few request paths with django-silk and run a simple background email task on the DB backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL |
| Tasks | django-tasks-db (DB backend) |
| Profiling | django-silk |
| Email | Console (dev) |
| Analytics | GoatCounter (env-driven, self-hosted) |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| DB safety | django-zeal, django-migration-linter, django-test-migrations |
| Dev extras | django-extensions |

## Setup

```sh
createdb silk_db
cp .env.example .env
# edit .env — set DJANGO_SECRET_KEY and DATABASE_URL if needed
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Web server
uv run manage.py runserver

# Background task worker (second terminal)
uv run manage.py db_worker
```

## Enqueue a task (Django shell)

```python
from jobs.tasks import send_welcome_email
result = send_welcome_email.enqueue("you@example.com")
print(result.id)
```

The worker terminal will print the email (console backend).

## Profiling

Visit any page, then open <http://localhost:8000/silk/> to see the request profile.

To profile a specific function, use the context-manager form inside a task or view:

```python
from django.conf import settings

if settings.DEBUG:
    from silk.profiling.profiler import silk_profile
else:
    def silk_profile(*_a, **_kw):
        def deco(fn): return fn
        return deco
```

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## Test

```sh
uv run pytest
```

## Migration lint

```sh
uv run manage.py lintmigrations
```

## Analytics (GoatCounter)

Set in `.env`:

```sh
ANALYTICS_HOST=https://<code>.goatcounter.com
ANALYTICS_ID=<code>
```

The snippet is suppressed when `DEBUG=True` — no beacons in dev.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

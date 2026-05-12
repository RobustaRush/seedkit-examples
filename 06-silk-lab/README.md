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

Profile request paths with django-silk and run background email tasks on the database backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL (psycopg v3) |
| Background tasks | django-tasks-db (DB backend, no broker) |
| Profiling | django-silk (`/silk/`) |
| Analytics | GoatCounter (self-hosted, env-driven) |
| Email (local) | console backend |
| Health checks | `/healthz`, `/readyz` |
| Dev tools | django-extensions, django-zeal, django-migration-linter, django-test-migrations |
| Lint | Ruff |
| Tests | pytest + pytest-django |

## Prerequisites

- Python ≥ 3.12
- uv
- PostgreSQL running locally

## Setup

```sh
createdb silk_db
cp .env.example .env
# edit .env — at minimum set DJANGO_SECRET_KEY (or leave the generated one)
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Web server
uv run manage.py runserver

# Background task worker (separate terminal)
uv run manage.py db_worker
```

## Profiling

Open `http://localhost:8000/silk/` while `DEBUG=True`. Every request is
recorded automatically. To profile a specific code block:

```python
from django.conf import settings

if settings.DEBUG:
    from silk.profiling.profiler import silk_profile
else:
    def silk_profile(*_a, **_kw):
        def deco(fn): return fn
        return deco

@silk_profile(name="my expensive operation")
def expensive_operation():
    ...
```

Clear accumulated data:

```sh
uv run manage.py silk_clear_request_log
```

## Background tasks

Enqueue the sample task from the shell:

```sh
uv run manage.py shell_plus
>>> from jobs.tasks import send_welcome_email
>>> send_welcome_email.enqueue("you@example.com")
```

Add your own tasks to `jobs/tasks.py`:

```python
from django.tasks import task

@task()
def my_task(arg: str) -> None:
    ...
```

## Analytics (GoatCounter)

Set in `.env`:

```sh
ANALYTICS_ID=mysite
ANALYTICS_HOST=https://mysite.goatcounter.com
```

The snippet fires only when `ANALYTICS_ID` and `ANALYTICS_HOST` are both set and `DEBUG=False`.

## Health checks

```sh
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready  (or 503 if DB unreachable)
```

## Lint & format

```sh
uv run ruff check .
uv run ruff format .
```

## Migration safety

```sh
uv run manage.py lintmigrations
```

## Tests

```sh
uv run pytest
```

`django-test-migrations` is installed — import the `migrator` fixture in any test file to write migration forward/rollback tests.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

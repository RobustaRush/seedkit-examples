## Prompt

```
/seedkit

Project name: 06-silk-lab
Purpose: profile a few request paths with django-silk and run a simple background email task on the DB backend.

Settings layout: split.
Database: PostgreSQL.
Postgres location: on the host (use `createdb silk_db`).
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
| Framework | Django 6 |
| Database | PostgreSQL (`silk_db`) |
| Settings | Split — `base` / `local` / `production` / `test` |
| Profiling | django-silk (`/silk/`) |
| Tasks | Django Tasks — database backend (`db_worker`) |
| Email | Console backend in dev (`EMAIL_URL=consolemail://`) |
| Analytics | GoatCounter (env-driven, dev-suppressed) |
| Health | `/healthz` (liveness) · `/readyz` (readiness) |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Dev extras | django-extensions · django-zeal · django-migration-linter · django-test-migrations |

## Setup

```sh
# 1. Create the database
createdb silk_db

# 2. Copy env and set a real secret key
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY, DATABASE_URL

# 3. Install dependencies
uv sync

# 4. Apply migrations
uv run manage.py migrate

# 5. Create a superuser
uv run manage.py createsuperuser
```

## Running

```sh
# Dev server
uv run manage.py runserver

# Task worker (second terminal)
uv run manage.py db_worker
```

## Enqueue a task

```python
# In shell_plus or a view:
from jobs.tasks import send_welcome_email
result = send_welcome_email.enqueue("user@example.com")
```

The worker picks it up and prints the email to stdout (console backend).

## Profiling with Silk

Hit any view while the dev server is running, then open:

```
http://localhost:8000/silk/
```

Request and SQL timings appear immediately. The `send_welcome_email` task also wraps its body in a `silk_profile` context manager — run the worker to see the profile row.

## Lint

```sh
uv run ruff check .
uv run ruff format --check .
```

## Tests

```sh
uv run pytest
```

`django-test-migrations` is installed — add migration tests to `jobs/tests.py` using the `migrator` fixture.

## Migration safety

```sh
uv run manage.py lintmigrations
```

Exits non-zero on dangerous operations (NOT NULL without default, missing rollback, etc.).

## Health checks

- `GET /healthz` → `ok` (liveness — no DB hit)
- `GET /readyz` → `ready` (readiness — requires DB)

## Key URLs

| URL | Description |
|---|---|
| `/admin/` | Django admin |
| `/silk/` | Silk profiling dashboard (DEBUG only) |
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

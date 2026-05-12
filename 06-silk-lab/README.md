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

Profile request paths with **django-silk** and run background tasks via Django Tasks (DB backend).

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL (`silk_db`) |
| Settings | Split — `base` / `local` / `production` / `test` |
| Request handling | WSGI |
| Background tasks | `django-tasks-db` — worker: `manage.py db_worker` |
| Profiling | django-silk (`/silk/`, `@silk_profile`) |
| Email | Console backend in local |
| Analytics | GoatCounter (self-hosted, env-driven) |
| Health checks | `/healthz` (liveness), `/readyz` (DB check) |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Dev extras | django-extensions, django-zeal, django-migration-linter, django-test-migrations |

## Setup

```sh
createdb silk_db
cp .env.example .env   # edit DATABASE_URL if your Postgres user/password differ
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Dev server
uv run manage.py runserver

# Task worker (second terminal)
uv run manage.py db_worker
```

## Enqueue a task

```sh
uv run manage.py shell_plus
```

```python
from jobs.tasks import send_welcome_email
result = send_welcome_email.enqueue("you@example.com")
print(result.status)
```

## Profiling

- **All requests**: visit `http://localhost:8000/silk/` after any page load.
- **Function-level**: `send_welcome_email` wraps its body in `silk_profile(name="send_welcome_email")` — check `/silk/` after enqueueing.
- Clear accumulated data: `uv run manage.py silk_clear_request_log`

## Lint & test

```sh
uv run ruff check .
uv run ruff format .
uv run pytest
uv run manage.py lintmigrations
```

## Health checks

```sh
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

## Analytics (GoatCounter)

Set in `.env`:

```sh
ANALYTICS_HOST=https://<yoursite>.goatcounter.com
ANALYTICS_ID=<yoursite>
```

The snippet fires only when `DEBUG=False` and both vars are set.

## Key URLs (local)

| URL | Purpose |
|---|---|
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:8000/silk/` | Silk profiling dashboard |
| `http://localhost:8000/healthz` | Liveness probe |
| `http://localhost:8000/readyz` | Readiness probe |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

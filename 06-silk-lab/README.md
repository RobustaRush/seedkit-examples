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

Run the foundation, the boot check, start `manage.py db_worker` in a second terminal, enqueue one example task and confirm it runs. Hit a profiled view and confirm the request appears under `/silk/`. Run `uv run manage.py lintmigrations`. Run `uv run pytest` to confirm the test runner is wired (no project-specific tests required — `django-test-migrations` is installed for the user to write migration tests later).
```

---

# 06-silk-lab

Profile request paths with django-silk and run background email tasks on the DB backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (host) |
| Profiling | django-silk (`/silk/`) |
| Background tasks | django-tasks + DB backend (`db_worker`) |
| Email (dev) | Console (`consolemail://`) |
| Analytics | GoatCounter (env-driven, skipped in dev) |
| Healthchecks | `/healthz`, `/readyz` |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| DB safety | django-zeal, django-migration-linter, django-test-migrations |
| Dev toolbox | django-extensions |

## Setup

```sh
createdb silk_db
cp .env.example .env
# Edit .env: set DJANGO_SECRET_KEY to a real value
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Terminal 1
uv run manage.py runserver

# Terminal 2 — task worker
uv run manage.py db_worker
```

## Enqueue an example task

```python
# uv run manage.py shell_plus
from jobs.tasks import send_example_email
send_example_email.enqueue("you@example.com")
```

## Profiling

Visit any page, then open **http://localhost:8000/silk/** to see the request profile. The home view at `/` is decorated with `@silk_profile(name="home")`.

## Key commands

```sh
uv run manage.py lintmigrations       # check migrations for unsafe ops
uv run ruff check .                   # lint
uv run ruff format .                  # format
uv run pytest                         # tests
uv run manage.py show_urls            # list all URL patterns
uv run manage.py silk_clear_request_log  # clear silk data
```

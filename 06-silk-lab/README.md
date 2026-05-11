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

Run the foundation, the boot check, start `manage.py db_worker` in a second terminal, enqueue one example task and confirm it runs. Hit a profiled view and confirm the request appears under `/silk/`. Run `uv run manage.py lintmigrations`. Run `uv run pytest` to confirm the test runner is wired (no project-specific tests required — `django-test-migrations` is installed for the user to write migration tests later).
```

---

# 06-silk-lab

Profile request paths with django-silk and run background email tasks via the Django Tasks DB backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL (psycopg3) |
| Settings | Split (base / local / production / test) |
| Profiling | django-silk (`/silk/`) |
| Background tasks | django-tasks-db (`db_worker`) |
| Email | console backend in dev |
| Analytics | GoatCounter snippet (env-driven, `ANALYTICS_ID`) |
| Health checks | `/healthz` (liveness), `/readyz` (readiness) |
| Dev tools | django-extensions, django-zeal, django-migration-linter, django-test-migrations |
| Lint | Ruff |
| Tests | pytest + pytest-django |

## Local setup

```sh
createdb silk_db
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY to a real value
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Web server
uv run manage.py runserver

# Background worker (second terminal)
uv run manage.py db_worker
```

Open <http://localhost:8000/admin/> and <http://localhost:8000/silk/>.

## Enqueue an example task

```python
from pages.tasks import send_welcome_email
send_welcome_email.enqueue("you@example.com")
```

## Commands

```sh
uv run manage.py migrate
uv run manage.py lintmigrations
uv run ruff check .
uv run ruff format .
uv run pytest
uv run manage.py show_urls
uv run manage.py shell_plus
```

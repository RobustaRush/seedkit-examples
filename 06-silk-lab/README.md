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

| Component | Package |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (psycopg) |
| Settings | Split (base / local / production / test) |
| Profiling | django-silk (`/silk/`) |
| Background tasks | django-tasks-db (`db_worker`) |
| Email | Console (dev) |
| Analytics | GoatCounter (self-hosted snippet, env-driven) |
| Health checks | `/healthz`, `/readyz` |
| Extensions | django-extensions (`show_urls`, `shell_plus`) |
| DB safety | django-zeal · django-migration-linter · django-test-migrations |
| Lint | Ruff |
| Tests | pytest + pytest-django |

## Setup

```sh
createdb silk_db
cp .env.example .env          # then fill in DJANGO_SECRET_KEY
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Terminal 1 — web server
uv run manage.py runserver

# Terminal 2 — task worker
uv run manage.py db_worker
```

## Enqueue a task (shell)

```sh
uv run manage.py shell_plus
>>> from jobs.tasks import send_welcome_email
>>> result = send_welcome_email.enqueue("user@example.com")
>>> result.status   # check after db_worker picks it up
```

## URLs

| Path | Purpose |
|---|---|
| `/admin/` | Django admin |
| `/silk/` | Silk profiling dashboard (DEBUG only) |
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe (checks DB) |

## Lint & test

```sh
uv run ruff check .
uv run ruff format .
uv run pytest
uv run manage.py lintmigrations
```

## GoatCounter analytics

Set `ANALYTICS_HOST` and `ANALYTICS_ID` in `.env` to activate. The snippet fires only when `DEBUG=False` and both vars are non-empty.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

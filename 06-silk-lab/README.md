## Prompt

```
/seedkit-slim

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

Profile a few request paths with django-silk and run a simple background email task on the DB backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.x |
| Settings | Split (base / local / production) |
| Database | PostgreSQL (`silk_db`) |
| Profiling | django-silk (`/silk/`) |
| Background tasks | django-tasks + django-tasks-db (`db_worker`) |
| Email | Console backend (local) |
| Analytics | GoatCounter (self-hosted, env-driven) |
| Extensions | django-extensions (`show_urls`, shell_plus, …) |
| Linter | Ruff |
| Tests | pytest + pytest-django + django-test-migrations |
| DB safety | django-zeal (N+1), django-migration-linter, django-test-migrations |

## Setup

```sh
createdb silk_db
cp .env.example .env   # already pre-filled for local dev
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

Terminal 1 — web server:

```sh
uv run manage.py runserver
```

Terminal 2 — task worker:

```sh
uv run manage.py db_worker
```

## Enqueue a task

```python
# manage.py shell
from jobs.tasks import send_welcome_email
result = send_welcome_email.enqueue("you@example.com")
print(result.status)
```

## Profiling

Visit any page (admin, healthz, etc.) then open `/silk/` to inspect request timelines and SQL.

Use `@silk_profile` on any view function:

```python
from silk.profiling.profiler import silk_profile

@silk_profile(name="my-view")
def my_view(request):
    ...
```

## GoatCounter

Set `GOATCOUNTER_SITE_CODE=<your-site-code>` in `.env` and extend `templates/base.html` in your views. The JS snippet is only emitted when the env var is non-empty.

## Key commands

```sh
uv run manage.py show_urls
uv run manage.py lintmigrations
uv run ruff check .
uv run pytest
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

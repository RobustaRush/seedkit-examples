## Prompt

```
/seedkit

Project name: 01-minimal-blog
Purpose: a tiny blog to verify the skill works end-to-end.

Settings layout: single file (`config/settings.py`).
Database: SQLite.
Local dev mode: uv on host.
Lint with Ruff: no.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none (vanilla `django.contrib.auth`).
Structured logging: no.
Task runner: none.
Add-ons:
  - email: console backend (`EMAIL_URL=consolemail://`).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: no (this case is the bare floor — no extra views).
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.

Production setup: skip.

Run the foundation, the boot check (migrate + createsuperuser), and confirm /admin/ login works.
```

---

# 01-minimal-blog

A tiny blog to verify the skill works end-to-end.

## Stack

- Django 6 · SQLite · uv on host
- Email: console backend (stdout)
- Auth: vanilla `django.contrib.auth`

## Setup

```sh
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY to a real value for production.
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in with the superuser credentials.

## Commands

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Migrate | `uv run manage.py migrate` |
| Run dev server | `uv run manage.py runserver` |
| Run tests | `uv run manage.py test` |
| Collect static | `uv run manage.py collectstatic --noinput` |

## Environment variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django secret key (required in production) |
| `DJANGO_DEBUG` | `True` for dev, unset or `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `DATABASE_URL` | DB URL (defaults to `db.sqlite3` when `DEBUG=True`) |
| `EMAIL_URL` | Email backend URL (defaults to `consolemail://` in dev) |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

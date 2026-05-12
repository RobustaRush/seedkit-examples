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

| Component | Choice |
|-----------|--------|
| Framework | Django 6 |
| Database | SQLite (file: `db.sqlite3`) |
| Settings | Single file (`config/settings.py`) |
| Request handling | WSGI |
| Dev mode | uv on host |
| Email | Console backend (`consolemail://`) |

## Setup

```sh
cp .env.example .env
# Edit .env and set a real DJANGO_SECRET_KEY for anything beyond local dev
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in with your superuser credentials.

## Test

```sh
uv run manage.py test
```

## Dependencies

See `pyproject.toml` for pinned versions.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

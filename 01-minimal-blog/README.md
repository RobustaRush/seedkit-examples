## Prompt

```
/seedkit

Project name: 01-minimal-blog
Purpose: a tiny blog to verify the skill works end-to-end.

Settings layout: single file (`config/settings.py`).
Database: SQLite.
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

A tiny blog to verify the seedkit skill works end-to-end.

## Stack

| Layer | Choice |
|---|---|
| Python | >=3.12 |
| Framework | Django 6 |
| Database | SQLite |
| Settings | Single file (`config/settings.py`) via django-environ |
| Auth | Vanilla `django.contrib.auth` |
| Email | Console backend (dev) |

## Getting started

```sh
cp .env.example .env
# Edit .env — set a real DJANGO_SECRET_KEY for production

uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Then open <http://127.0.0.1:8000/admin/> and sign in.

## Key commands

| Command | Purpose |
|---|---|
| `uv run manage.py migrate` | Apply database migrations |
| `uv run manage.py createsuperuser` | Create an admin user |
| `uv run manage.py runserver` | Start the development server |
| `uv run manage.py test` | Run the test suite |
| `uv run manage.py collectstatic --noinput` | Collect static files |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

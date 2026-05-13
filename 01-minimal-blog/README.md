## Prompt

```
/seedkit-slim

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

A tiny blog to verify the seedkit-slim skill works end-to-end.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 5.x (WSGI) |
| Database | SQLite |
| Settings | `config/settings.py` (single file) |
| Auth | `django.contrib.auth` (vanilla) |
| Email | Console backend (`EMAIL_URL=consolemail://`) |
| Tests | `manage.py test` |

## Key commands

```sh
# Install deps
uv sync

# Apply migrations
uv run manage.py migrate

# Create superuser
uv run manage.py createsuperuser

# Run dev server
uv run manage.py runserver

# Run tests
uv run manage.py test
```

## Environment

Copy `.env` and adjust as needed. Required variables:

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | insecure dev key | Must be changed in production |
| `DEBUG` | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | `*` | Restrict in production |
| `EMAIL_URL` | `consolemail://` | Prints email to console |

## Admin

Visit `/admin/` after `migrate` + `createsuperuser`.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

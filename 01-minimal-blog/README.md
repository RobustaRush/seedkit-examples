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

A tiny blog scaffold — smallest path to a working Django project.

## Stack

- Django 6.x
- SQLite
- django-environ (env-driven settings)
- Console email backend

## Setup

```sh
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY to a real value
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open http://127.0.0.1:8000/admin/ and log in.

## Key commands

```sh
uv run manage.py migrate          # apply migrations
uv run manage.py createsuperuser  # create admin user
uv run manage.py runserver        # start dev server
uv run manage.py test             # run tests
```

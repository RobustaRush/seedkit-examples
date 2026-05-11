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

A tiny Django blog scaffold — the bare floor used to verify the seedkit skill works end-to-end.

## Stack

- Django 6.x
- django-environ (env-driven settings)
- SQLite (local)
- Email: console backend (`EMAIL_URL=consolemail://`)
- uv on host

## Setup

```sh
cp .env.example .env          # edit DJANGO_SECRET_KEY with a real key
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/>.

## Key commands

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Run migrations | `uv run manage.py migrate` |
| Run dev server | `uv run manage.py runserver` |
| Run tests | `uv run manage.py test` |

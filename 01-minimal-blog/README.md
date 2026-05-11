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

A minimal Django blog skeleton used to verify the seedkit skill end-to-end.

## Stack

| Layer | Choice |
|---|---|
| Python | >=3.12 (uv on host) |
| Django | >=6.0,<7.0 |
| Settings | single `config/settings.py` + `django-environ` |
| Database | SQLite (dev) |
| Email | console backend (`consolemail://`) |
| Auth | vanilla `django.contrib.auth` |

## Setup

```sh
cp .env.example .env
# Edit .env and set a real DJANGO_SECRET_KEY for production.
uv sync
```

## Commands

```sh
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
uv run manage.py test
```

Open <http://127.0.0.1:8000/admin/> and log in with your superuser credentials.

## Environment variables

See `.env.example` for the full list. Key vars:

| Variable | Dev default | Required in prod |
|---|---|---|
| `DJANGO_SECRET_KEY` | `django-insecure-build-only` | yes |
| `DJANGO_DEBUG` | `False` | set to `False` |
| `DJANGO_ALLOWED_HOSTS` | `[]` | yes |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | yes |
| `EMAIL_URL` | `consolemail://` | yes |
| `DEFAULT_FROM_EMAIL` | `webmaster@localhost` | yes |

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

A tiny Django blog — minimal scaffold to verify the seedkit skill works end-to-end.

## Stack

| Layer | Choice |
|---|---|
| Runtime | Python ≥ 3.12, managed by uv |
| Framework | Django 6.x |
| Settings | `config/settings.py` (single file, django-environ) |
| Database | SQLite (default: `db.sqlite3` in project root) |
| Email | Console backend (prints to stdout) |
| Static files | `STATIC_ROOT = staticfiles/` |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed on the host

## Setup

```sh
cp .env.example .env
# Edit .env — set a real DJANGO_SECRET_KEY before running in production
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in with the superuser you created.

## Test

```sh
uv run manage.py test
```

## Environment variables

See `.env.example` for the full list. Key variables:

| Variable | Default (dev) | Required in prod |
|---|---|---|
| `DJANGO_SECRET_KEY` | `django-insecure-build-only` | Yes |
| `DJANGO_DEBUG` | `False` | Set to `False` |
| `DJANGO_ALLOWED_HOSTS` | `[]` | Yes |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Yes |
| `EMAIL_URL` | `consolemail://` | Yes |
| `DEFAULT_FROM_EMAIL` | `webmaster@localhost` | Yes |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

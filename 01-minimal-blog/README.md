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

| Layer | Choice |
|---|---|
| Runtime | Python ≥ 3.12 via uv |
| Framework | Django 6.x |
| Settings | Single `config/settings.py` with `django-environ` |
| Database | SQLite (`db.sqlite3`) |
| Email | Console backend (`consolemail://`) |
| Auth | Vanilla `django.contrib.auth` |

## Setup

```sh
cp .env.example .env
# Edit .env and set a real DJANGO_SECRET_KEY for production
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in.

## Environment variables

See `.env.example` for the full list. Key variables:

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_DEBUG` | `False` | Set `True` in dev |
| `DJANGO_SECRET_KEY` | *(required in prod)* | Use `secrets.token_urlsafe(50)` |
| `DJANGO_ALLOWED_HOSTS` | `[]` | Comma-separated; DEBUG skips this check |
| `DATABASE_URL` | `sqlite:///db.sqlite3` in DEBUG | 4-slash absolute path |
| `EMAIL_URL` | `consolemail://` in DEBUG | Prints to stdout |

## Commands

```sh
uv run manage.py migrate          # apply migrations
uv run manage.py createsuperuser  # create admin user
uv run manage.py runserver        # local dev server
uv run manage.py test             # run tests
uv run manage.py collectstatic --noinput  # collect static files
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

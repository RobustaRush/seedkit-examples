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

A tiny Django blog — minimal scaffold to verify seedkit-slim works end-to-end.

## Stack

| Layer | Choice |
|---|---|
| Python | 3.12 |
| Django | 6.0 |
| Database | SQLite |
| Request handling | WSGI |
| Settings | Single file (`config/settings.py`) |
| Auth | Vanilla `django.contrib.auth` |
| Email | Console backend |
| Task runner | None |

## Key commands

```sh
# Install dependencies
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

## Access

- Admin: http://127.0.0.1:8000/admin/
- Root `/` redirects to `/admin/`

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

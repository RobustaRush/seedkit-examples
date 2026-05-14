## Prompt

```
/seedkit-slim

Project name: 05-orbit-demo
Purpose: scratch project to exercise django-orbit and verify outbound mail flows are captured.

Settings layout: single file.
Database: SQLite.
Lint with Ruff: yes.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: no.
Task runner: none.
Add-ons:
  - debug: django-orbit (observability dashboard + MCP)
  - email: console backend in local, plus Mailpit running in Docker for richer inspection
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.
Run the foundation + boot check. Spin up Mailpit via a one-service `docker-compose.yml`, point Django at SMTP `localhost:1025`, send a test mail, and confirm it appears in Mailpit's UI on `:8025`.
```

---

# 05-orbit-demo

Scratch project to exercise django-orbit and verify outbound mail flows are captured.

## Stack

| Layer | Choice |
|---|---|
| Runtime | Python 3.14, Django 6.0, WSGI |
| Database | SQLite |
| Debug dashboard | django-orbit 0.8.1 (+ MCP) |
| Dev email | Mailpit (Docker) — SMTP :1025, UI :8025 |
| Lint | Ruff |
| Tests | `manage.py test` |

## Quick start

```sh
cp .env.example .env          # edit DJANGO_SECRET_KEY if desired
docker compose up -d --wait   # start Mailpit
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

| URL | What |
|---|---|
| http://127.0.0.1:8000/admin/ | Django admin |
| http://127.0.0.1:8000/orbit/ | Orbit dashboard (DEBUG only) |
| http://127.0.0.1:8000/healthz | Liveness probe → `ok` |
| http://127.0.0.1:8000/readyz | Readiness probe → `ready` |
| http://127.0.0.1:8025/ | Mailpit UI |

## Send a test email

```sh
uv run manage.py shell -c "
from django.core.mail import send_mail
send_mail('hello', 'body', 'from@example.com', ['to@example.com'])
"
```

Then open http://127.0.0.1:8025/ — the message appears under **Messages**.

## Lint

```sh
uv run ruff check .
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

## Prompt

```
/seedkit

Project name: 05-orbit-demo
Purpose: scratch project to exercise django-orbit and verify outbound mail flows are captured.

Settings layout: single file.
Database: SQLite.
Local dev mode: uv on host.
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
| Runtime | Python ≥ 3.12, uv on host |
| Framework | Django 6 |
| Database | SQLite |
| Debug toolbar | django-orbit (+ MCP) |
| Email (local) | Mailpit via Docker (SMTP :1025, UI :8025) |
| Lint | Ruff |
| Tests | manage.py test |

## Setup

```sh
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY to a real value for anything beyond dev
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Start Mailpit (captures outbound mail)
docker compose up -d --wait mailpit

# Start Django
uv run manage.py runserver
```

## Key URLs

| URL | What |
|---|---|
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/orbit/ | Orbit observability dashboard |
| http://localhost:8000/healthz | Liveness probe → `ok` |
| http://localhost:8000/readyz | Readiness probe → `ready` |
| http://localhost:8025 | Mailpit web UI |

## Send a test mail

```sh
uv run manage.py shell -c "
from django.core.mail import send_mail
send_mail('hello', 'body', 'from@example.com', ['to@example.com'])
"
```

Then open http://localhost:8025 — the message appears immediately.

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## MCP (AI assistant integration)

Add to `claude_desktop_config.json` (`~/Library/Application Support/Claude/`):

```json
{
  "mcpServers": {
    "django-orbit": {
      "command": "uv",
      "args": ["run", "manage.py", "orbit_mcp"],
      "cwd": "/path/to/05-orbit-demo",
      "env": {"DJANGO_SETTINGS_MODULE": "config.settings"}
    }
  }
}
```

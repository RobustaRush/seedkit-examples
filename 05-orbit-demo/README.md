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

| Component | Choice |
|-----------|--------|
| Framework | Django 6.x |
| Database | SQLite |
| Settings | Single file (`config/settings.py`) |
| Dev mode | uv on host |
| Debug dashboard | django-orbit (`/orbit/`) |
| Email (dev) | Mailpit via Docker (`localhost:8025`) |
| Health checks | `/healthz`, `/readyz` |
| Lint | Ruff |
| Tests | `manage.py test` |

## Setup

```sh
cp .env.example .env
# Edit .env — set a real DJANGO_SECRET_KEY for production
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

- Admin: http://localhost:8000/admin/
- Orbit dashboard: http://localhost:8000/orbit/
- Mailpit UI: http://localhost:8025/

## Email

`EMAIL_URL=smtp://localhost:1025` in `.env` routes all outbound mail through Mailpit.
Every sent message appears instantly in the Mailpit web UI at `:8025`.

For production, replace with a real SMTP URL in `.env`:

```sh
EMAIL_URL=smtp+tls://user:pass@smtp.example.com:587
DEFAULT_FROM_EMAIL=no-reply@example.com
```

## django-orbit MCP (AI assistant integration)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

## Commands

```sh
# Lint
uv run ruff check .
uv run ruff format .

# Tests
uv run manage.py test

# Migrate
uv run manage.py migrate

# Shell
uv run manage.py shell

# Send a test mail (Mailpit must be running)
uv run manage.py shell -c "
from django.core.mail import send_mail
send_mail('hello', 'body', 'from@example.com', ['to@example.com'])
"
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

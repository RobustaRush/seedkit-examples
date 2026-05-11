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

- Django 6 · SQLite · uv on host
- **django-orbit** — observability dashboard + MCP server at `/orbit/`
- **Mailpit** — local SMTP capture UI at `http://localhost:8025`
- **Ruff** — lint + format
- Health check endpoints: `/healthz`, `/readyz`

## Setup

```sh
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY to something random for dev

uv sync --group dev
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

Start Mailpit (captures outbound email):

```sh
docker compose up -d
```

Start Django:

```sh
uv run manage.py runserver
```

## URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8000/admin/` | Django admin |
| `http://localhost:8000/orbit/` | Orbit observability dashboard |
| `http://localhost:8000/healthz` | Liveness probe |
| `http://localhost:8000/readyz` | Readiness probe (checks DB) |
| `http://localhost:8025/` | Mailpit web UI |

## Send a test email

```sh
DJANGO_SETTINGS_MODULE=config.settings uv run python -c "
import django; django.setup()
from django.core.mail import send_mail
send_mail('Test', 'Hello from orbit-demo', 'from@example.com', ['to@example.com'])
"
```

Then open `http://localhost:8025` to see it captured.

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## Test

```sh
uv run manage.py test
```

## Orbit MCP (AI assistant integration)

Add to `claude_desktop_config.json`:

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

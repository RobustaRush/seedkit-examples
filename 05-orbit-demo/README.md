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

- **Django** 6.x
- **django-orbit** (observability dashboard + MCP) — `/orbit/`
- **Mailpit** (dev mail catcher) — Docker, port 8025 UI / 1025 SMTP
- **Ruff** (lint + format)
- SQLite, uv on host

## Setup

```sh
cp .env.example .env
# Edit DJANGO_SECRET_KEY in .env
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Start Mailpit
docker compose up -d mailpit

# Start Django
uv run manage.py runserver
```

- Admin: http://localhost:8000/admin/
- Orbit dashboard: http://localhost:8000/orbit/
- Mailpit UI: http://localhost:8025/
- Liveness: http://localhost:8000/healthz
- Readiness: http://localhost:8000/readyz

## Email

In dev, `EMAIL_URL=smtp://localhost:1025` sends all mail to Mailpit.  
Switch to `consolemail://` if you want stdout-only output without Docker.

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## Test

```sh
uv run manage.py test
```

## Orbit MCP

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

## Cleanup

```sh
docker compose down -v
```

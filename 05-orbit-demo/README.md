## Prompt

```
/seedkit

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

- Django 6 · SQLite · single-file settings · django-environ
- django-orbit (observability dashboard + MCP) at `/orbit/`
- Mailpit for local email inspection (Docker) at `http://localhost:8025`
- Ruff (lint + format)
- Health checks: `/healthz` (liveness) · `/readyz` (readiness)

## Setup

```sh
cp .env.example .env
# edit DJANGO_SECRET_KEY if needed
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

## Mailpit

Start the Mailpit container before running the server if you want emails captured in the UI:

```sh
docker compose up -d mailpit
```

Open <http://localhost:8025> to inspect captured emails.
The `.env` default points Django's SMTP at `localhost:1025` (Mailpit).
Without Mailpit running, set `EMAIL_URL=consolemail://` in `.env` to fall back to console output.

## Orbit MCP

To connect Claude Desktop to the live telemetry stream, add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

| Command | What it does |
|---|---|
| `uv run manage.py migrate` | Apply migrations |
| `uv run manage.py runserver` | Start dev server |
| `uv run manage.py test` | Run tests |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `docker compose up -d mailpit` | Start Mailpit |
| `docker compose down -v` | Stop and clean up |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

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

Scratch project to exercise `django-orbit` and verify outbound mail flows are captured.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.x |
| Database | SQLite (file `db.sqlite3`) |
| Observability | django-orbit 0.8.x — dashboard at `/orbit/` |
| Email (dev) | SMTP → Mailpit (Docker) — web UI at `http://localhost:8025` |
| Lint | Ruff |
| Tests | `manage.py test` (stock Django) |

## Setup

```sh
cp .env.example .env          # then edit DJANGO_SECRET_KEY
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Start Mailpit (captures outgoing SMTP)
docker compose up -d --wait

# Start Django
uv run manage.py runserver
```

- Admin: <http://localhost:8000/admin/>
- Orbit dashboard: <http://localhost:8000/orbit/>
- Mailpit inbox: <http://localhost:8025/>
- Liveness: <http://localhost:8000/healthz>
- Readiness: <http://localhost:8000/readyz>

## Send a test mail

```sh
uv run manage.py shell -c "
from django.core.mail import send_mail
send_mail('hello', 'body', 'from@example.com', ['to@example.com'])
"
```

Check <http://localhost:8025> — the message appears immediately.

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## Test

```sh
uv run manage.py test
```

## MCP (AI assistant integration)

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

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

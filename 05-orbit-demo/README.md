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

Scratch project to exercise `django-orbit` (observability dashboard + MCP) and verify outbound mail flows are captured via Mailpit.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.x |
| Database | SQLite (dev) |
| Request handling | WSGI (gunicorn in prod) |
| Debug dashboard | `django-orbit` at `/orbit/` |
| Email (dev) | SMTP → Mailpit (`localhost:1025`) |
| Email (prod) | Set `EMAIL_URL` env var |
| Health checks | `/healthz` (liveness), `/readyz` (readiness) |
| Linter | Ruff |

## Setup

```sh
cp .env.example .env
# edit .env — set a real DJANGO_SECRET_KEY
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

## Mailpit (local email inspection)

Captures all outgoing SMTP. Open <http://localhost:8025> to view mail.

```sh
docker compose up -d mailpit
# EMAIL_URL=smtp://localhost:1025 must be set in .env (already the default)
```

## Orbit (observability dashboard)

`http://localhost:8000/orbit/` — requests, SQL, logs, exceptions, cache, ORM events, emails.

**MCP integration** (AI assistants query live telemetry):

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

## Health checks

```sh
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

## Lint

```sh
uv run ruff check .
uv run ruff format --check .
```

## Test

```sh
uv run manage.py test
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

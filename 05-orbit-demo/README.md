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
| Runtime | Python ≥ 3.12, uv |
| Framework | Django 6 |
| Database | SQLite (dev + default) |
| Request handling | WSGI (gunicorn in prod) |
| Observability | django-orbit dashboard + MCP |
| Email (dev) | Mailpit via Docker SMTP on `localhost:1025` |
| Email (fallback) | console backend |
| Health checks | `/healthz`, `/readyz` |
| Lint | Ruff |

## Install

```sh
cp .env.example .env
# Edit DJANGO_SECRET_KEY in .env
uv sync
uv run manage.py migrate
```

## Run

```sh
# Start Mailpit (captures outbound mail at http://localhost:8025)
docker compose up -d --wait

# Start Django
uv run manage.py runserver
```

## Useful URLs (dev)

| URL | Purpose |
|---|---|
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/orbit/ | Orbit observability dashboard |
| http://localhost:8025/ | Mailpit web UI |
| http://localhost:8000/healthz | Liveness probe |
| http://localhost:8000/readyz | Readiness probe |

## Email

Django is pointed at Mailpit's SMTP port (`localhost:1025`) via `EMAIL_URL=smtp://localhost:1025` in `.env`.
All outbound mail is captured in the Mailpit UI — no real email is sent.

To send a test mail:

```sh
uv run manage.py shell -c "
from django.core.mail import send_mail
send_mail('hello', 'body', 'from@example.com', ['to@example.com'])
"
```

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## Test

```sh
uv run manage.py test
```

## django-orbit MCP (optional)

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

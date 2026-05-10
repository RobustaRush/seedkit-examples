# 05-orbit-demo

Scratch project exercising django-orbit observability dashboard and Mailpit mail capture.

## Stack

| Component | Package |
|-----------|---------|
| Framework | Django 6.x |
| Settings | django-environ (single file) |
| Database | SQLite (dev) |
| Debug dashboard | django-orbit[mcp] |
| Email (dev) | Console backend / Mailpit |
| Health checks | `/healthz`, `/readyz` |
| Lint | Ruff |

## Setup

```sh
cp .env.example .env        # edit DJANGO_SECRET_KEY
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
uv run manage.py runserver
```

- Admin: http://localhost:8000/admin/
- Orbit dashboard: http://localhost:8000/orbit/
- Health: http://localhost:8000/healthz

## Mailpit (local email inspection)

```sh
docker compose up -d mailpit
```

Set in `.env`:

```sh
EMAIL_URL=smtp://localhost:1025
```

Mailpit UI: http://localhost:8025

## MCP (AI assistant integration)

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

## Commands

```sh
uv run manage.py migrate
uv run manage.py test
uv run ruff check .
uv run ruff format .
```

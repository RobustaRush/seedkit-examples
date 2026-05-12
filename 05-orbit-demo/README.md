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

Scratch project to exercise **django-orbit** (observability dashboard + MCP) and verify
outbound mail flows are captured via **Mailpit**.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Settings | Single `config/settings.py` via `django-environ` |
| Database | SQLite (`db.sqlite3`) |
| Dev mode | uv on host |
| Observability | django-orbit — dashboard at `/orbit/`, MCP at `manage.py orbit_mcp` |
| Email (dev) | SMTP → Mailpit on `localhost:1025`; fallback `consolemail://` |
| Health checks | `/healthz` (liveness), `/readyz` (readiness + DB probe) |
| Lint | Ruff |

## Quick start

```sh
cp .env.example .env         # then edit DJANGO_SECRET_KEY
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://localhost:8000/admin/> and sign in.

## Mailpit (local mail inspection)

Requires Docker.

```sh
docker compose up -d mailpit
```

Point Django at Mailpit by setting in `.env`:

```sh
EMAIL_URL=smtp://localhost:1025
```

Open <http://localhost:8025> to view captured emails.

Send a test message:

```sh
uv run manage.py shell -c "
from django.core.mail import send_mail
send_mail('hello', 'body', 'from@example.com', ['to@example.com'])
"
```

## Orbit dashboard

Requires `DEBUG=True`.

- Dashboard: <http://localhost:8000/orbit/>
- Stats: <http://localhost:8000/orbit/stats/>

### MCP integration (Claude Desktop)

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

## Key commands

| Task | Command |
|---|---|
| Install deps | `uv sync` |
| Run dev server | `uv run manage.py runserver` |
| Migrate | `uv run manage.py migrate` |
| Create superuser | `uv run manage.py createsuperuser` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Tests | `uv run manage.py test` |
| Start Mailpit | `docker compose up -d mailpit` |
| Stop Mailpit | `docker compose down` |

## Dependencies

See `pyproject.toml` for pinned versions. Runtime: `django`, `django-environ`.
Dev: `django-orbit[mcp]`, `ruff`.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

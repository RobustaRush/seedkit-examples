## Prompt

```
/seedkit-slim

Project name: 04-media-vault
Purpose: media-heavy app where uploads land in S3, processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

Settings layout: split.
Database: PostgreSQL.
Request handling: asgi+channels.
Postgres location: Postgres-in-Docker (`db` service in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: none.
Add-ons:
  - redis
  - storage: S3-compatible (use MinIO in local Compose; configure via env)
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - real-time channel layer: `channels-redis` (reuse the same Redis service). Add an `EchoConsumer` (`AsyncJsonWebsocketConsumer`) that echoes received JSON back to the sender, routed at `/ws/echo/` in `config/routing.py`. Wire `config/asgi.py` with `ProtocolTypeRouter` + `AllowedHostsOriginValidator` + `AuthMiddlewareStack`.
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - CORS: yes.
  - REST API: `django-modern-rest` with the `msgspec` + `openapi` extras (`uv add 'django-modern-rest[msgspec,openapi]'`). Create an `api` app (`uv run manage.py startapp api`) with a single `MediaController` exposing `POST /api/media/` that accepts `{ "filename": str, "size": int }` (msgspec.Struct) and returns `{ "uid": uuid, "filename": str }`. Wire the `Router` from `api/urls.py` into `config/urls.py` under the `api` namespace. Do NOT add `dmr` to `INSTALLED_APPS`.
  - Frontend: none.
  - Devcontainer: yes.
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.

Production setup: skip.

Generate `docker-compose.yml` with services `db`, `redis`, `minio` (local services only — Django, the rqworker, and uvicorn run on the host). Run the foundation, `docker compose up -d`, `uv run uvicorn config.asgi:application --reload --host 0.0.0.0` (HTTP + WS share one process in dev — `manage.py runserver` doesn't upgrade WebSockets), `uv run manage.py rqworker default` in a separate terminal, migrate, createsuperuser, and confirm a sample task enqueues and a WebSocket round-trip works.
```

---

# 04-media-vault

Media-heavy app where uploads land in S3, processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.x + Channels (ASGI) |
| Database | PostgreSQL 16 |
| Task queue | django-tasks-rq (RQ + Redis) |
| WebSockets | channels-redis channel layer |
| Storage | django-storages (S3/MinIO) |
| Logging | structlog (pretty dev / JSON prod) |
| API | django-modern-rest (msgspec) |
| CORS | django-cors-headers |
| Lint | Ruff |
| Types | Pyright + django-stubs |

## Local services

```sh
docker compose up -d   # db, redis, minio
```

## Run

```sh
# Terminal 1 — HTTP + WebSocket server
uv run uvicorn config.asgi:application --reload --host 0.0.0.0

# Terminal 2 — task worker
uv run manage.py rqworker default
```

## First-time setup

```sh
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Key endpoints

| Path | Description |
|------|-------------|
| `/admin/` | Django admin |
| `/api/media/` | POST — create media record |
| `/ws/echo/` | WebSocket echo |
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe (checks DB) |
| `/django-rq/` | RQ dashboard |

## MinIO console

`http://127.0.0.1:9001` — credentials `minioadmin / minioadmin`

Create the `media-vault` bucket before uploading files.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

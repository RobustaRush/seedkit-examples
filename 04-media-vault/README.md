## Prompt

```
/seedkit

Project name: 04-media-vault
Purpose: media-heavy app where uploads land in S3, processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

Settings layout: split.
Database: PostgreSQL.
Request handling: asgi+channels.
Local dev mode: docker-compose (full stack: web + db + redis).
Docker structure: simple (separate `Dockerfile.dev`, single `docker-compose.yml`).
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
  - real-time channel layer: `channels-redis` (reuse the same Redis service). Add an `EchoConsumer` (`AsyncJsonWebsocketConsumer`) that echoes received JSON back to the sender, routed at `/ws/echo/` in `config/routing.py`. Wire `config/asgi.py` with `ProtocolTypeRouter` + `AllowedHostsOriginValidator` + `AuthMiddlewareStack` per `references/realtime.md`.
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - CORS: yes.
  - REST API: `django-modern-rest` with the `msgspec` + `openapi` extras (`uv add 'django-modern-rest[msgspec,openapi]'`). Create an `api` app (`uv run manage.py startapp api`) with a single `MediaController` exposing `POST /api/media/` that accepts `{ "filename": str, "size": int }` (msgspec.Struct) and returns `{ "uid": uuid, "filename": str }`. Wire the `Router` from `api/urls.py` into `config/urls.py` under the `api` namespace. Do NOT add `dmr` to `INSTALLED_APPS`.
  - Frontend: none.
  - Devcontainer: yes.
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.

Production setup: skip.

Generate `docker-compose.yml` with services `web`, `db`, `redis`, `worker`, `minio`. `web` runs `gunicorn -k uvicorn.workers.UvicornWorker config.asgi:application` (uvicorn worker since the foundation picked ASGI; HTTP and WS share the same process in dev). Run the foundation, `docker compose up -d`, migrate, createsuperuser, and confirm both a sample task enqueues and a WebSocket round-trip works.
```

---

# 04-media-vault

Media-heavy app where uploads land in S3, processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

## Stack

| Component | Technology |
|---|---|
| Framework | Django 6 (ASGI + channels) |
| Database | PostgreSQL 17 |
| Cache | Redis 7 (django-redis, DB 0) |
| Channel layer | channels-redis (DB 1) |
| Background tasks | django-tasks + django-tasks-rq (RQ, DB 3) |
| Storage | S3-compatible (MinIO in dev, any S3 in prod) |
| REST API | django-modern-rest (msgspec + openapi) |
| Structured logging | structlog + django-structlog |
| Server | gunicorn + UvicornWorker |
| Lint | Ruff |
| Types | pyright + django-stubs |

## Quick start

```sh
cp .env.example .env
# edit .env — set a real DJANGO_SECRET_KEY
docker compose up -d --wait
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

MinIO console: <http://localhost:9001/> (credentials from `.env`).

## Key commands

```sh
# Migrate
docker compose exec web uv run manage.py migrate

# Run tests
docker compose exec web uv run manage.py test

# Lint
uv run ruff check .

# Type check
uv run pyright

# Worker logs
docker compose logs -f worker

# Tear down (removes volumes)
docker compose down -v
```

## Services

| Service | Port | Purpose |
|---|---|---|
| `web` | 8000 | HTTP + WebSocket (gunicorn + UvicornWorker) |
| `db` | — | PostgreSQL (internal only) |
| `redis` | — | Cache / channel layer / RQ broker (internal only) |
| `worker` | — | RQ worker (`manage.py rqworker default`) |
| `minio` | 9000, 9001 | S3-compatible object store |

## API

`POST /api/media/` — accept `{"filename": str, "size": int}`, return `{"uid": uuid, "filename": str}`.

Missing `size` returns 422.

## WebSocket

Connect to `ws://localhost:8000/ws/echo/` with `Origin: http://localhost`. Any JSON sent is echoed back.

## Health checks

- `GET /healthz` → `ok` (liveness)
- `GET /readyz` → `ready` (readiness — DB probe)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

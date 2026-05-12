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

- **Django 6** · ASGI + channels · PostgreSQL · Redis
- **Channels + channels-redis** — WebSocket support (`/ws/echo/`)
- **django-tasks-rq** — background jobs via Redis Queue
- **django-storages[s3]** — S3-compatible storage (MinIO in dev)
- **django-modern-rest** — REST API (`POST /api/media/`)
- **structlog** — structured JSON logging in production, pretty in dev
- **django-cors-headers** — CORS support
- **Ruff** — linting + formatting
- **pyright + django-stubs** — type checking
- Local dev: **docker-compose** (web + db + redis + worker + minio)

## Quick start

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>

## Key commands

```sh
# Start all services
docker compose up -d

# Migrate
docker compose exec web uv run manage.py migrate

# Run tests
docker compose exec web uv run manage.py test

# Lint
docker compose exec web uv run ruff check .

# Format
docker compose exec web uv run ruff format .

# Type check (on host)
uv run pyright

# Tail logs
docker compose logs -f web worker

# MinIO console
open http://localhost:9001   # user: minioadmin / minioadmin
```

## Services

| Service | URL |
|---|---|
| Web (Django) | http://localhost:8000 |
| Admin | http://localhost:8000/admin/ |
| REST API | http://localhost:8000/api/media/ |
| WebSocket echo | ws://localhost:8000/ws/echo/ |
| Health | http://localhost:8000/healthz |
| Readiness | http://localhost:8000/readyz |
| RQ dashboard | http://localhost:8000/django-rq/ |
| MinIO console | http://localhost:9001 |

## Background tasks

Tasks are defined in `jobs/tasks.py`. The worker picks them up from Redis queue `default`.

```python
from jobs.tasks import process_upload
result = process_upload.enqueue("some-uid")
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

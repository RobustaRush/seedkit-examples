## Prompt

```
/seedkit

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

Generate `docker-compose.yml` with services `db`, `redis`, `minio` (local services only — Django, the rqworker, and uvicorn run on the host). Run the foundation, `docker compose up -d`, `uv run uvicorn config.asgi:application --reload --host 0.0.0.0` (HTTP + WS share one process in dev — `manage.py runserver` doesn't upgrade WebSockets), `uv run manage.py rqworker default` in a separate terminal, migrate, createsuperuser, and confirm a sample task enqueues and a WebSocket round-trip works.
```

---

# 04-media-vault

Media-heavy app where uploads land in S3, processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.0 |
| Database | PostgreSQL 17 (Docker) |
| Request handling | ASGI + channels (uvicorn) |
| Task queue | django-tasks-rq (Redis) |
| Channel layer | channels-redis |
| Storage | S3-compatible (MinIO in dev) |
| REST API | django-modern-rest (msgspec) |
| Logging | structlog (pretty dev / JSON prod) |

## Prerequisites

- Python 3.12+
- uv
- Docker + Docker Compose

## Setup

```sh
cp .env.example .env
# Edit .env — set a real DJANGO_SECRET_KEY
docker compose up -d --wait        # start db, redis, minio
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
# Terminal 1 — HTTP + WebSocket server
uv run uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000

# Terminal 2 — background task worker
uv run manage.py rqworker default
```

Open <http://localhost:8000/admin/> and sign in.

## API

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/media/` | `{"filename": str, "size": int}` | `{"uid": uuid, "filename": str}` |

## WebSocket

Connect to `ws://localhost:8000/ws/echo/` — sends back every JSON message unchanged.

## Health checks

| URL | Behaviour |
|---|---|
| `/healthz` | Always 200 `ok` (liveness) |
| `/readyz` | 200 `ready` when DB is reachable; 503 otherwise |

## Services

| Service | Local URL |
|---|---|
| Django / uvicorn | <http://localhost:8000> |
| MinIO API | <http://localhost:9000> |
| MinIO Console | <http://localhost:9001> (user: minioadmin / minioadmin) |

## Test

```sh
uv run manage.py test
```

## Lint / format

```sh
uv run ruff check .
uv run ruff format .
```

## Type check

```sh
uv run pyright
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

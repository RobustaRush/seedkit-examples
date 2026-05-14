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

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| DB | PostgreSQL (Docker) |
| Request handling | ASGI + channels (uvicorn) |
| Background tasks | Django Tasks + django-tasks-rq (RQ backend) |
| Real-time | django-channels + channels-redis, `EchoConsumer` at `/ws/echo/` |
| Storage | S3-compatible (MinIO locally via docker-compose) |
| Cache | django-redis (`/0`) |
| REST API | django-modern-rest (msgspec), `POST /api/media/` |
| Email | console in dev |
| CORS | django-cors-headers |
| Logging | structlog — pretty in dev, JSON in prod |
| Lint | Ruff |
| Types | pyright + django-stubs |

## Local setup

```sh
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY, adjust other values as needed

docker compose up -d          # db (5433), redis (6379), minio (9000/9001)

uv run manage.py migrate
uv run manage.py createsuperuser

# HTTP + WebSocket (one process in dev — manage.py runserver won't upgrade WS)
uv run uvicorn config.asgi:application --reload --host 0.0.0.0

# Background task worker (separate terminal)
uv run manage.py rqworker default
```

Open <http://localhost:8000/admin/> and sign in.

## Key commands

| Command | Description |
|---|---|
| `uv run manage.py migrate` | Apply DB migrations |
| `uv run manage.py createsuperuser` | Create admin user |
| `uv run uvicorn config.asgi:application --reload` | Run dev server (HTTP + WS) |
| `uv run manage.py rqworker default` | Run background task worker |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `uv run pyright` | Type check |
| `uv run manage.py test` | Run tests |

## Endpoints

| Path | Description |
|---|---|
| `/admin/` | Django admin |
| `/api/media/` | `POST {"filename": str, "size": int}` → `{"uid": uuid, "filename": str}` |
| `/ws/echo/` | WebSocket echo (requires `Origin` header matching `ALLOWED_HOSTS`) |
| `/healthz` | Liveness probe (returns `ok`) |
| `/readyz` | Readiness probe — checks DB (returns `ready`) |
| `/django-rq/` | RQ dashboard |

## MinIO (local S3)

Console at <http://localhost:9001> (login: `minioadmin` / `minioadmin`).

To enable S3 storage locally, set in `.env`:

```sh
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_STORAGE_BUCKET_NAME=media-vault
AWS_S3_ENDPOINT_URL=http://localhost:9000
AWS_S3_URL_PROTOCOL=http:
```

Create the bucket in the MinIO console first, or via `mc`:

```sh
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/media-vault
```

## Settings

| File | Used when |
|---|---|
| `config/settings/base.py` | Shared base |
| `config/settings/local.py` | Dev (`manage.py` / uvicorn on host) |
| `config/settings/production.py` | Prod (set `DJANGO_SETTINGS_MODULE=config.settings.production`) |
| `config/settings/test.py` | Tests (`manage.py test`) |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

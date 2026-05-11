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

Media-heavy Django app: uploads land in S3 (MinIO in local dev), processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Request handling | ASGI + django-channels (gunicorn + UvicornWorker) |
| Database | PostgreSQL 17 |
| Cache | Redis (django-redis) |
| Channel layer | channels-redis |
| Background tasks | django-tasks + RQ backend (django-tasks-rq) |
| Storage | S3-compatible — MinIO in dev, any S3 in prod |
| REST API | django-modern-rest (msgspec + openapi extras) |
| Logging | structlog (pretty in dev / JSON in prod) |
| Lint | Ruff |
| Types | pyright + django-stubs |
| Dev env | docker-compose (web, worker, db, redis, minio) |

## Local dev

```sh
cp .env.example .env          # set DJANGO_SECRET_KEY to something real
docker compose up -d --build  # starts web, worker, db, redis, minio
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

## Key URLs

| URL | Purpose |
|---|---|
| `/admin/` | Django admin |
| `/api/media/` | `POST` — create media record |
| `/ws/echo/` | WebSocket echo endpoint |
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe (checks DB) |
| `/django-rq/` | RQ dashboard (admin-gated) |

## API — POST /api/media/

Request:
```json
{ "filename": "photo.jpg", "size": 102400 }
```

Response `201`:
```json
{ "uid": "...", "filename": "photo.jpg" }
```

## Background tasks

Tasks live in `jobs/tasks.py`. Add `@task()`-decorated functions; they're
auto-imported by `JobsConfig.ready()`. Enqueue from anywhere:

```python
from jobs.tasks import process_upload
result = process_upload.enqueue("photo.jpg", 102400)
```

Worker runs `python manage.py rqworker default` (the `worker` compose service).

## S3 / MinIO

In local dev, the `minio` service is the S3-compatible target. Create the
bucket once after first `docker compose up`:

```sh
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mc mb local/media-vault
```

Or open the MinIO console at <http://localhost:9001> (user/pass: `minioadmin`).

Set `AWS_STORAGE_BUCKET_NAME=media-vault` in `.env` to activate S3 storage.

## Lint and type-check

```sh
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Tests

```sh
docker compose exec web uv run manage.py test
```

## Adding a dependency

```sh
uv add somepkg
docker compose build
docker compose up -d
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

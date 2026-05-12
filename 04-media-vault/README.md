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

Media-heavy Django app: uploads land in S3-compatible storage (MinIO in dev), background processing runs as Redis-queued tasks, and clients subscribe over WebSockets for status updates.

## Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12, Django 6, ASGI + django-channels |
| Server | gunicorn + UvicornWorker |
| Database | PostgreSQL 17 |
| Cache | Redis 7 (django-redis) |
| Task queue | django-tasks-rq (RQ backend) + django-rq admin |
| Storage | S3-compatible via django-storages (MinIO in dev) |
| WebSockets | channels-redis channel layer |
| REST API | django-modern-rest (msgspec + openapi) |
| Logging | structlog — pretty in dev, JSON in prod |
| Lint | Ruff |
| Types | pyright + django-stubs |

## Local development

### Prerequisites

- Docker + Docker Compose
- uv (`brew install uv`)

### First run

```sh
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY to a real value (or generate one):
# uv run python -c "import secrets; print(secrets.token_urlsafe(50))"

docker compose up -d --build --wait
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser --username admin --email admin@example.com
```

Open <http://localhost:8000/admin/>.

MinIO console: <http://localhost:9001> (user/pass from `.env` `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`).

Create the storage bucket (once, after MinIO is running):

```sh
uv run python -c "
import boto3, os
s3 = boto3.client('s3', endpoint_url='http://127.0.0.1:9000',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin'),
    region_name='us-east-1')
s3.create_bucket(Bucket='media-vault')
print('bucket ready')
"
```

### Day-to-day commands

```sh
# Lint
uv run ruff check .
uv run ruff format .

# Type check
uv run pyright

# Tests
docker compose exec web uv run manage.py test

# Migrations
docker compose exec web uv run manage.py makemigrations
docker compose exec web uv run manage.py migrate

# Enqueue a sample task from a shell
docker compose exec web uv run manage.py shell -c "
from jobs.tasks import process_media
result = process_media.enqueue('test-uid-1234', 'photo.jpg')
print('job id:', result.id)
"
```

### Services

| Service | URL |
|---|---|
| Django app | <http://localhost:8000> |
| Admin | <http://localhost:8000/admin/> |
| RQ dashboard | <http://localhost:8000/django-rq/> |
| Health | <http://localhost:8000/healthz> |
| Readiness | <http://localhost:8000/readyz> |
| MinIO console | <http://localhost:9001> |

### API

`POST /api/media/` — register a new media upload.

Request:
```json
{"filename": "photo.jpg", "size": 102400}
```

Response `201`:
```json
{"uid": "e88c281b-...", "filename": "photo.jpg"}
```

### WebSocket echo

Connect to `ws://localhost:8000/ws/echo/` (requires `Origin: http://localhost`). Every JSON message is echoed back verbatim. Used for verifying the channel layer is live before wiring real consumers.

```sh
uv run python -c "
import asyncio, json, websockets
async def main():
    async with websockets.connect('ws://localhost:8000/ws/echo/', origin='http://localhost') as ws:
        await ws.send(json.dumps({'text': 'hello'}))
        print(await ws.recv())
asyncio.run(main())
"
```

## Project layout

```
config/
  settings/
    base.py        — shared settings (all add-ons wired here)
    local.py       — dev overrides (currently just base import)
    production.py  — prod overrides (S3 static)
  asgi.py          — ProtocolTypeRouter: HTTP + WebSocket
  routing.py       — WebSocket URL patterns
  urls.py          — HTTP URL patterns
api/               — django-modern-rest MediaController
chat/              — EchoConsumer (WebSocket)
jobs/              — sample @task (process_media)
pages/             — /healthz + /readyz views
```

## Adding a dependency

```sh
uv add somepkg
docker compose build web worker
docker compose up -d
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

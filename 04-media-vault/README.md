## Prompt

```
/seedkit

Project name: 04-media-vault
Purpose: media-heavy app where uploads land in S3 and processing runs as Redis-queued background tasks.

Settings layout: split.
Database: PostgreSQL.
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
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`)
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - CORS: yes.
  - REST API: `django-modern-rest` with the `msgspec` + `openapi` extras (`uv add 'django-modern-rest[msgspec,openapi]'`). Create an `api` app (`uv run manage.py startapp api`) with a single `MediaController` exposing `POST /api/media/` that accepts `{ "filename": str, "size": int }` (msgspec.Struct) and returns `{ "uid": uuid, "filename": str }`. Wire the `Router` from `api/urls.py` into `config/urls.py` under the `api` namespace. Do NOT add `dmr` to `INSTALLED_APPS`.
  - Frontend: none.
  - Devcontainer: yes.
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.

Production setup: skip.

Generate `docker-compose.yml` with services `web`, `db`, `redis`, `worker`, `minio`. Run the foundation, `docker compose up -d`, migrate, createsuperuser, and confirm a sample task enqueues and completes.
```

---

# 04-media-vault

Media-heavy Django app — uploads land in S3-compatible storage (MinIO in local dev), processing runs as Redis-queued background tasks via `django-tasks-rq`.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 7 |
| Object storage | S3-compatible (MinIO in dev) |
| Background tasks | django-tasks-rq (RQ backend) |
| REST API | django-modern-rest (msgspec + openapi) |
| Logging | structlog (pretty dev / JSON prod) |
| Lint | Ruff |
| Types | pyright + django-stubs |
| Dev env | Docker Compose |

## Quick start

```sh
cp .env.example .env          # adjust DJANGO_SECRET_KEY
docker compose up -d --wait   # starts web, worker, db, redis, minio
docker compose exec -T web uv run manage.py migrate
docker compose exec -T web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/> to confirm the admin works.

MinIO console: <http://localhost:9001> (minioadmin / minioadmin).

## Key URLs

| URL | Description |
|---|---|
| `/admin/` | Django admin |
| `/api/media/` | `POST` — register a media upload |
| `/django-rq/` | RQ dashboard (worker queue stats) |
| `/healthz` | Liveness probe — returns `ok` |
| `/readyz` | Readiness probe — checks DB |

## API

```sh
# Register a media upload
curl -sf -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "photo.jpg", "size": 204800}'
# → {"uid": "...", "filename": "photo.jpg"}
```

## Development

```sh
# Lint
docker compose exec -T web uv run ruff check .
docker compose exec -T web uv run ruff format .

# Type check (on host)
uv run pyright

# Tests
docker compose exec -T web uv run manage.py test

# Tail logs
docker compose logs -f web worker
```

## Adding a dependency

```sh
uv add somepkg            # updates pyproject.toml + uv.lock on host
docker compose build web worker
docker compose up -d
```

## MinIO bucket setup

The `.env.example` sets `AWS_STORAGE_BUCKET_NAME=media`. Create the bucket once:

```sh
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mc mb local/media
docker compose exec minio mc anonymous set download local/media
```

Or use the MinIO console at <http://localhost:9001>.

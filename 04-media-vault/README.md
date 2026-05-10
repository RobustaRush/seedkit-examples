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

Media-heavy Django app where uploads land in S3-compatible storage and processing runs as Redis-queued background tasks.

## Stack

- **Django 6** with split settings (base / local / production)
- **PostgreSQL 17** via `psycopg[binary]`
- **Redis 7** cache (`django-redis`) + RQ task queue (`django-tasks-rq`)
- **MinIO** (S3-compatible) via `django-storages[s3]`
- **structlog** — JSON in prod, pretty-print in dev, per-request `request_id`
- **django-modern-rest** (`msgspec` + `openapi` extras) — REST API
- **django-cors-headers** — CORS
- **Ruff** lint + format
- **pyright** + `django-stubs` type checking
- Docker Compose dev stack: `web`, `db`, `redis`, `worker`, `minio`

## Local dev

```sh
cp .env.example .env
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>

## Commands

```sh
# Lint
docker compose exec web uv run ruff check .

# Format
docker compose exec web uv run ruff format .

# Type check (host)
uv run pyright

# Tests
docker compose exec web uv run manage.py test

# Worker logs
docker compose logs -f worker
```

## MinIO

MinIO console: <http://localhost:9001> (login: `minioadmin` / `minioadmin`)

Create the bucket before uploading:

```sh
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mc mb local/media-vault
```

Or create it via the MinIO web UI at <http://localhost:9001>.

## REST API

```sh
# Create a media record (happy path)
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "photo.jpg", "size": 1024}'

# Invalid body — returns 422
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "photo.jpg"}'
```

## Health checks

```sh
curl http://127.0.0.1:8000/healthz   # → ok
curl http://127.0.0.1:8000/readyz    # → ready
```

## Adding a dependency

```sh
uv add somepkg
docker compose build web worker
docker compose up -d
```

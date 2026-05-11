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

Media-heavy Django app where uploads land in S3 and processing runs as Redis-queued background tasks.

## Stack

- **Django** — web framework (split settings: base / local / production)
- **PostgreSQL** — primary database (psycopg3)
- **Redis** — cache (db/0) + task queue (db/3 via RQ)
- **MinIO** — S3-compatible object storage (local dev); swap env vars for AWS S3 / R2 / Spaces in prod
- **django-tasks-rq** — Django Tasks API backed by Redis Queue
- **django-modern-rest** — typed REST API with msgspec + OpenAPI
- **structlog** — JSON logging in prod, pretty console in dev, per-request `request_id`
- **django-cors-headers** — CORS for cross-origin frontends
- **django-storages[s3]** — S3 media storage
- **Ruff** — linter + formatter
- **Pyright + django-stubs** — static type checking

## Local dev (docker-compose)

```sh
cp .env.example .env           # already done; edit DJANGO_SECRET_KEY
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open http://localhost:8000/admin

MinIO console: http://localhost:9001 (minioadmin / minioadmin)

## Key commands

```sh
# Lint
docker compose exec web uv run ruff check .

# Format
docker compose exec web uv run ruff format .

# Type check (run on host)
uv run pyright

# Run tests
docker compose exec web uv run manage.py test

# Enqueue a task manually
docker compose exec web uv run manage.py shell -c \
  "from api.tasks import process_media; process_media.enqueue('test-uid')"
```

## API

`POST /api/media/` — register a media upload intent

```json
{"filename": "a.png", "size": 1234}
```

Returns `{"uid": "<uuid>", "filename": "a.png"}`.

## Health checks

- `GET /healthz` → `ok` (liveness — no DB)
- `GET /readyz` → `ready` (readiness — checks DB)

## Adding a dependency

```sh
uv add somepkg
docker compose build web worker
docker compose up -d
```

## Environment variables

See `.env.example` for the full list. Key vars:

| Var | Description |
|---|---|
| `DATABASE_URL` | Postgres connection URL |
| `REDIS_URL` | Redis base URL (no trailing slash) |
| `AWS_ACCESS_KEY_ID` | S3 / MinIO access key |
| `AWS_SECRET_ACCESS_KEY` | S3 / MinIO secret |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name |
| `AWS_S3_ENDPOINT_URL` | Non-AWS endpoint (e.g. `http://minio:9000`) |
| `EMAIL_URL` | Email backend URL (`consolemail://` in dev) |

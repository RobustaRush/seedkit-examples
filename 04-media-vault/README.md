# 04-media-vault

Media-heavy app where uploads land in S3 and processing runs as Redis-queued background tasks.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6.x |
| Database | PostgreSQL 17 (psycopg 3) |
| Cache | Redis 7 (django-redis) |
| Storage | S3-compatible — MinIO in dev, any S3 provider in prod |
| Tasks | django-tasks + django-tasks-rq (Redis Queue backend) |
| REST API | django-modern-rest (msgspec + openapi) |
| Logging | structlog (pretty in dev, JSON in prod) |
| Lint | Ruff |
| Types | pyright + django-stubs |
| Dev env | docker-compose (web, db, redis, worker, minio) |

## Local development

```sh
cp .env.example .env          # already done; contains dev defaults
docker compose up -d --build  # starts all five services
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Admin: http://localhost:8000/admin/
MinIO console: http://localhost:9001/ (minioadmin / minioadmin)

## Key commands

```sh
# Lint
docker compose exec web uv run ruff check .

# Type check
docker compose exec web uv run pyright

# Tests
docker compose exec web uv run manage.py test

# Worker (already started by docker compose)
docker compose exec worker uv run manage.py rqworker default

# Health checks
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

## REST API

```sh
# Create media entry
curl -X POST http://localhost:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "photo.jpg", "size": 1024}'

# Missing field → 422
curl -X POST http://localhost:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "photo.jpg"}'
```

## Adding a dependency

```sh
uv add somepkg          # updates pyproject.toml + uv.lock
docker compose build web worker
docker compose up -d
```

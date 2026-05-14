# 08-fly-app

Production Django app deployed to Fly.io with multi-stage Docker image and S3-compatible object storage.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (Docker locally, Fly Postgres in prod) |
| Cache / broker | Redis |
| Background tasks | Celery |
| Object storage | S3-compatible (MinIO locally, any S3 provider in prod) |
| Auth | django-mail-auth (passwordless magic-link) |
| Auth hardening | django-axes (brute-force lockout) |
| Email | django-anymail / Postmark (prod); console (dev) |
| REST API | django-bolt (fast-path settings) |
| Analytics | Google Analytics 4 |
| Error reporting | GlitchTip via sentry-sdk |
| Task runner | mise |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Type checks | pyright + django-stubs |
| Deploy | Fly.io |

## Quick start

```sh
# First time
mise trust && mise install
cp .env.example .env        # then fill in DJANGO_SECRET_KEY

docker compose up -d db redis

mise run migrate
mise run superuser          # interactive
mise run dev
```

## Task runner (mise)

| Command | What it does |
|---|---|
| `mise run dev` | `uv run manage.py runserver` |
| `mise run migrate` | Apply migrations |
| `mise run makemigrations` | Create new migration |
| `mise run shell` | Django shell |
| `mise run superuser` | Create superuser (interactive) |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run collectstatic` | Collect static files |
| `mise run worker` | Start Celery worker |
| `mise run runbolt` | Start django-bolt API server (port 8002) |
| `mise run deploy` | `fly deploy` |

Fallback without mise: use `uv run manage.py <cmd>` directly.

## Environment variables

Copy `.env.example` to `.env`. Required in production (empty = `ImproperlyConfigured` at startup):

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- `REDIS_URL`
- `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`
- `POSTMARK_SERVER_TOKEN`, `ANYMAIL_WEBHOOK_SECRET`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`

## Local services

`docker-compose.yml` runs Postgres (port 5432), Redis (port 6379), and MinIO (ports 9000/9001).

```sh
docker compose up -d          # all services
docker compose up -d db redis # minimal
```

MinIO console: http://localhost:9001 (credentials from `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in `.env`, default `minioadmin`/`minioadmin`).

## django-bolt API

Two servers run in development:

```sh
mise run dev      # Django (admin, auth) on port 8000
mise run runbolt  # Bolt API on port 8002 (config.settings.bolt fast-path)
```

Endpoints:
- `GET /users/{user_id}` — returns `{"id": ..., "username": "..."}` (JSON, async, ORM via `aget`)

## GDPR management commands

```sh
uv run manage.py export_user_data <user_id>   # GDPR Art. 20 data portability
uv run manage.py delete_user_data <user_id>   # GDPR Art. 17 right to erasure
```

## Deploy

```sh
fly launch --no-deploy
fly postgres create
fly postgres attach <db-name>
fly redis create
fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=<your-app>.fly.dev \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.fly.dev \
    POSTMARK_SERVER_TOKEN=<token> \
    ANYMAIL_WEBHOOK_SECRET=<secret> \
    DEFAULT_FROM_EMAIL=no-reply@example.com \
    SERVER_EMAIL=django@example.com \
    AWS_ACCESS_KEY_ID=<key> \
    AWS_SECRET_ACCESS_KEY=<secret> \
    AWS_STORAGE_BUCKET_NAME=<bucket>
fly deploy
```

Fly's `release_command` runs `python manage.py migrate && python manage.py collectstatic --noinput` before traffic switches over.

Three processes run in production (`fly.toml [processes]`):
- **web** — gunicorn on port 8000
- **worker** — Celery worker
- **bolt** — django-bolt API on port 8002 (uses `config.settings.bolt`)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

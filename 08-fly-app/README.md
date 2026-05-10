# 08-fly-app

Production Django app deployed to Fly.io with a multi-stage Docker image and S3-compatible object storage.

## Stack

- **Django** + **PostgreSQL** + **Redis**
- **Celery** (background tasks, broker = Redis)
- **django-mail-auth** (passwordless magic-link login)
- **django-axes** (brute-force lockout, cache-backed in prod)
- **django-bolt** (fast-path REST API via Rust/Actix)
- **django-storages[s3]** (MinIO in dev, S3 in prod)
- **anymail[postmark]** (transactional email)
- **GA4** analytics
- **GlitchTip** error reporting (sentry-sdk)
- **django-csp** (Content Security Policy)
- GDPR: `export_user_data` / `delete_user` management commands
- **Ruff** lint + format, **pyright** type checking, **pytest**

## Local dev

```sh
cp .env.example .env   # edit DJANGO_SECRET_KEY
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

Two servers in dev:
- `http://localhost:8000` — Django (admin, accounts, health checks)
- `http://localhost:8001` — Bolt API (start separately; see below)

### Start Bolt API

```sh
docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.bolt web \
  python manage.py runbolt --dev --port 8001
```

Then: `curl http://localhost:8001/users/1`

### Health checks

```sh
curl http://localhost:8000/healthz    # → ok
curl http://localhost:8000/readyz     # → ready
```

## Testing

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

## Deploy (Fly.io)

```sh
fly launch --no-deploy
fly postgres create && fly postgres attach <db-name>
fly redis create && fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=<your-app>.fly.dev \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.fly.dev \
    AWS_ACCESS_KEY_ID=... \
    AWS_SECRET_ACCESS_KEY=... \
    AWS_STORAGE_BUCKET_NAME=... \
    DEFAULT_FROM_EMAIL=no-reply@example.com \
    POSTMARK_SERVER_TOKEN=... \
    ANYMAIL_WEBHOOK_SECRET=... \
    SENTRY_DSN=...
fly deploy
```

Fly runs three processes from the same image:
- `web` — gunicorn (Django)
- `worker` — Celery worker
- `bolt` — `manage.py runbolt` with `DJANGO_SETTINGS_MODULE=config.settings.bolt`

## GDPR commands

```sh
python manage.py export_user_data <user_id> > data.json
python manage.py delete_user <user_id>
```

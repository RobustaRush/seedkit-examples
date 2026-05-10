# 08-fly-app

Production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

## Stack

- Django 6 · PostgreSQL · Redis
- Celery (background tasks)
- S3-compatible storage (MinIO locally, AWS S3 in prod)
- django-mail-auth (passwordless magic-link login)
- django-axes (brute-force lockout)
- django-bolt (fast-path JSON API)
- Anymail / Postmark (transactional email)
- GlitchTip via sentry-sdk (error reporting)
- django-csp (Content Security Policy)
- GA4 analytics
- GDPR: PII scrubbing, export/delete commands

## Local development

```sh
cp .env.example .env
# Set DJANGO_SECRET_KEY in .env
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

Health checks:
```sh
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

### Bolt fast-path API

```sh
# In a separate terminal:
docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.bolt web \
  uv run manage.py runbolt --dev
# → http://127.0.0.1:8001/users/1
```

### Adding a dependency

```sh
uv add somepkg
docker compose build web
docker compose up -d
```

## Tests

```sh
uv run pytest
uv run ruff check .
uv run pyright
```

## GDPR commands

```sh
uv run manage.py export_user_data <user_id>
uv run manage.py delete_user <user_id>
```

## Deploy to Fly.io

```sh
fly launch --no-deploy
fly postgres create && fly postgres attach <db-name>
fly redis create && fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=<your-app>.fly.dev \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.fly.dev \
    POSTMARK_SERVER_TOKEN=<token> \
    DEFAULT_FROM_EMAIL=no-reply@example.com \
    SERVER_EMAIL=django@example.com \
    AWS_ACCESS_KEY_ID=<key> \
    AWS_SECRET_ACCESS_KEY=<secret> \
    AWS_STORAGE_BUCKET_NAME=<bucket>
fly deploy
```

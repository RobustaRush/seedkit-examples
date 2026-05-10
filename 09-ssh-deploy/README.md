# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

- **Django 6** · split settings (base / local / production / test)
- **PostgreSQL 17** · psycopg (binary)
- **Redis 7** · django-redis cache · django-tasks-rq background tasks
- **structlog** · JSON in prod / pretty in dev · per-request `request_id`
- **Umami** · self-hosted analytics (env-driven website ID and host)
- **Bugsink** · self-hosted error reporting (sentry-sdk DSN)
- **django-csp** · Content Security Policy (production only)
- **Ruff** · lint + format
- **pytest + pytest-django** · test runner
- **GitHub Actions** · CI (test) + deploy via SSH

## Local development

```sh
cp .env.example .env   # edit DJANGO_SECRET_KEY
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000/admin/

## Key commands

```sh
# Lint
uv run ruff check .
uv run ruff format .

# Tests
uv run pytest

# Background worker (dev — already in docker-compose.override.yml)
python manage.py rqworker default

# Health checks
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

## Production deploy

Triggered automatically on push to `main` via `.github/workflows/deploy.yml`.

Required GitHub repo secrets:
- `SSH_HOST` — VPS IP or hostname
- `SSH_USER` — SSH user on the VPS
- `SSH_KEY` — private key (matching a key authorized on the VPS)
- `GHCR_TOKEN` — PAT with `read:packages` (used by the VPS to pull the image)

On the VPS:

```sh
git clone <repo> /srv/09-ssh-deploy
cp /srv/09-ssh-deploy/deploy/.env.prod.example /srv/09-ssh-deploy/deploy/.env.prod
# fill in all values, then:
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

## GDPR

```sh
python manage.py export_user_data <user_id> > data.json   # Article 20 export
python manage.py delete_user <user_id>                     # Article 17 deletion
```

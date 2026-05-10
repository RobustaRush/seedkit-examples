# 07-vps-saas

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy.

## Stack

- Django 6, split settings (local / production / test)
- PostgreSQL 17, Redis 7
- Celery (no Beat)
- django-allauth with MFA (TOTP)
- django-axes brute-force lockout
- WhiteNoise (static), media volume on VPS host
- structlog (JSON in prod, pretty in dev, request_id per request)
- sentry-sdk (production only)
- django-csp (production only)
- django-dbbackup → S3-compatible bucket
- Ruff, pytest, pyright, pre-commit

## Local dev

```sh
cp .env.example .env
# Edit .env and set a real DJANGO_SECRET_KEY
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

Health checks:

```sh
curl http://localhost:8000/healthz   # → ok
curl http://localhost:8000/readyz    # → ready
```

## Dev commands

```sh
uv run pytest               # run tests
uv run ruff check .         # lint
uv run ruff format .        # format
uv run pyright              # type check
uv run pre-commit install   # install git hooks
```

## Production deploy (VPS)

```sh
ssh user@vps
cd /srv/07-vps-saas
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml run --rm web python manage.py migrate
docker compose -f docker-compose.prod.yml up -d
```

## Database backups

Install `deploy/crontab` on the VPS host (see file for schedule). Requires S3 credentials in `.env.prod`:

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
DBBACKUP_BUCKET=...
```

Restore:

```sh
docker compose -f docker-compose.prod.yml exec web python manage.py dbrestore --database=default
```

## NTP note

TOTP 2FA requires accurate server time. Clock skew > 30 s will cause authentication failures. Ensure NTP is running on the VPS (`timedatectl status`).

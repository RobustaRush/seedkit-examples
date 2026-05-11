## Prompt

```
/seedkit

Project name: 07-vps-saas
Purpose: production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy.

Settings layout: split.
Database: PostgreSQL.
Local dev mode: docker-compose (full stack: web + db + redis).
Docker structure: simple (separate `Dockerfile.dev` for dev, single-stage production `Dockerfile`).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: yes.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login + mandatory verification).
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: none.
Add-ons:
  - redis
  - tasks: Celery (no Beat)
  - storage: WhiteNoise (static), media volume on the VPS host
  - email: SMTP in production, console backend in local. Use a placeholder Postmark URL (`EMAIL_URL=smtp+tls://<token>:<token>@smtp.postmarkapp.com:587`); also wire `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`, `DJANGO_ADMINS`.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: `django-axes` (yes), 2FA (yes).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings (HSTS, secure cookies, X-Frame, SSL redirect)
  - CSP via `django-csp`: yes
  - error reporting: Sentry SaaS (sentry-sdk)
  - CI: GitHub Actions test workflow
  - deploy target: VPS (Docker + Caddy)
  - database backups via `django-dbbackup`: yes
  - production Dockerfile: single-stage
Skip GDPR for this case.

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `Caddyfile`, `.github/workflows/test.yml`. Do not actually push to a remote VPS — just verify all artifacts are present and `docker build .` succeeds.
```

---

# 07-vps-saas

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Settings | Split (`base` / `local` / `production` / `test`) |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 7 |
| Task queue | Celery (no Beat) |
| Auth | django-allauth (email login, mandatory verification) |
| Auth hardening | django-axes + allauth.mfa (TOTP 2FA) |
| Static files | WhiteNoise (production) |
| Media | Docker named volume → served via Caddy |
| Logging | structlog (pretty dev / JSON prod, request_id) |
| Security | HSTS, secure cookies, X-Frame, CSP (django-csp) |
| Error reporting | Sentry SaaS (sentry-sdk) |
| Backups | django-dbbackup → S3-compatible |
| CI | GitHub Actions |
| Deploy | VPS · Docker Compose · Caddy |

## Local dev (docker-compose)

```sh
cp .env.example .env            # edit DJANGO_SECRET_KEY at minimum
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
# open http://localhost:8000/admin/
```

## Key commands

```sh
# Migrate
docker compose exec web uv run manage.py migrate

# Shell
docker compose exec web uv run manage.py shell

# Lint
uv run ruff check .
uv run ruff format .

# Tests
uv run pytest

# Type check
uv run pyright
```

## Health checks

| Path | Purpose |
|---|---|
| `/healthz` | Liveness — process alive, no external deps |
| `/readyz` | Readiness — DB reachable |

## Production deploy

```sh
# Build and push image (replace {owner})
docker build --build-arg GIT_SHA=$(git rev-parse --short HEAD) -t ghcr.io/{owner}/07-vps-saas:latest .
docker push ghcr.io/{owner}/07-vps-saas:latest

# On the VPS
ssh user@your-vps
cd /srv/07-vps-saas
cp .env.example .env.prod       # fill in all required values
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml run --rm web uv run manage.py migrate
docker compose -f docker-compose.prod.yml up -d
```

### Required production env vars

```sh
DJANGO_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com
DJANGO_BEHIND_PROXY=True
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com
DJANGO_SITE_DOMAIN=example.com

DATABASE_URL=postgres://postgres:<password>@db:5432/postgres
POSTGRES_PASSWORD=<strong-password>

REDIS_URL=redis://redis:6379

EMAIL_URL=smtp+tls://<token>:<token>@smtp.postmarkapp.com:587
DEFAULT_FROM_EMAIL=no-reply@example.com
SERVER_EMAIL=django@example.com
DJANGO_ADMINS=ops@example.com

SENTRY_DSN=<from sentry.io>

AWS_ACCESS_KEY_ID=<for dbbackup>
AWS_SECRET_ACCESS_KEY=<for dbbackup>
DBBACKUP_BUCKET=<your-backup-bucket>
```

## Database backups

```sh
# Manual backup
docker compose -f docker-compose.prod.yml exec web python manage.py dbbackup --clean

# Restore (destructive — confirm the target)
docker compose -f docker-compose.prod.yml exec web python manage.py dbrestore
```

Schedule via cron on the VPS host:

```cron
17 3 * * * django docker compose -f /srv/07-vps-saas/docker-compose.prod.yml exec -T web python manage.py dbbackup --clean
```

## Notes

- NTP must be accurate on the host — TOTP 2FA fails with clock skew > 30s.
- `Caddyfile` uses `example.com` — replace with your domain before deploying.
- `docker-compose.prod.yml` image tag uses `{owner}` — replace with your GitHub org/user.

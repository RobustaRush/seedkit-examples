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

- **Django** — core framework, split settings (base / local / production / test)
- **PostgreSQL** — primary database (psycopg3)
- **Redis** — cache (db/0), Celery broker (db/1), Celery results (db/2)
- **Celery** — background task queue (no Beat)
- **django-allauth[mfa]** — email login, mandatory verification in prod, TOTP 2FA
- **django-axes** — brute-force lockout (5 attempts / 1 h cooloff)
- **WhiteNoise** — static files; media served via host volume + Caddy
- **structlog** — JSON logs in prod, pretty console in dev, per-request `request_id`
- **django-csp** — Content Security Policy (production only)
- **sentry-sdk** — error reporting (set `SENTRY_DSN` to activate)
- **django-dbbackup** — nightly DB backups to S3-compatible storage
- **Ruff** — lint + format; **pyright** — type checks; **pytest** — test runner
- **Caddy 2** — TLS termination, media serving, health probes
- **GitHub Actions** — CI (test + lint + typecheck on every push)

## Local development

```sh
cp .env.example .env     # edit DJANGO_SECRET_KEY and DATABASE_URL if needed
docker compose up -d --wait --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createsuperuser
# open http://localhost:8000/admin/
```

## Commands

```sh
# Lint / format
uv run ruff check .
uv run ruff format .

# Type check
uv run pyright

# Tests
uv run pytest

# Migrations
uv run manage.py makemigrations
uv run manage.py migrate

# Shell
uv run manage.py shell
```

## Health checks

- `GET /healthz` → `200 ok` — liveness (no external deps)
- `GET /readyz` → `200 ready` — readiness (DB reachable)

## Production deploy (VPS)

```sh
ssh user@vps "cd /srv/07-vps-saas && git pull && \
  docker compose -f docker-compose.prod.yml pull && \
  docker compose -f docker-compose.prod.yml run --rm web uv run manage.py migrate && \
  docker compose -f docker-compose.prod.yml up -d"
```

Required prod env vars (`.env.prod`):
- `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`, `POSTGRES_PASSWORD`
- `REDIS_URL`
- `EMAIL_URL` (e.g. `smtp+tls://<token>:<token>@smtp.postmarkapp.com:587`)
- `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`, `DJANGO_ADMINS`
- `SENTRY_DSN` (optional)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DBBACKUP_BUCKET` (for backups)
- `DJANGO_BEHIND_PROXY=True` (Caddy terminates TLS)
- `DJANGO_SITE_DOMAIN` (shown in TOTP issuer)

## Database backups

```sh
# Manual backup
docker compose exec -T web python manage.py dbbackup --clean

# Manual restore (destructive!)
docker compose exec -T web python manage.py dbrestore --database=default
```

Cron on the VPS host (`/etc/cron.d/dbbackup`):
```
17 3 * * * django docker compose exec -T web python manage.py dbbackup --clean
```

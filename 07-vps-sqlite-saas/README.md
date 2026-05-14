## Prompt

```
/seedkit-slim

Project name: 07-vps-sqlite-saas
Purpose: production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

Settings layout: split.
Database: SQLite.
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: yes.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login + mandatory verification).
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: mise.
Add-ons:
  - cache backend: sqlite (separate `cache.sqlite3` + `CacheRouter` + `DatabaseCache`)
  - tasks: Django Tasks with the Database backend (`django-tasks-db`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
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
  - database backups: Litestream replication to S3-compatible storage; do not use `django-dbbackup`
  - production Dockerfile: multi-stage with the Litestream `.deb` installed in the prod stage; ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
Skip GDPR for this case.

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `Caddyfile`, `litestream.yml`, `entrypoint.sh`, `.github/workflows/test.yml`. Do not actually push to a remote VPS — just verify all artifacts are present and `docker build .` succeeds.
```

---

# 07-vps-sqlite-saas

Production-ready SaaS skeleton on a single VPS with SQLite, Litestream, Caddy, and Docker Compose. No external DB / cache / queue server required.

## Stack

| Layer | Choice |
|---|---|
| Runtime | Python 3.12, Django 5 |
| Database | SQLite (`db.sqlite3`) + Litestream → S3 |
| Cache | SQLite (`cache.sqlite3`) via `DatabaseCache` |
| Tasks | django-tasks-db (DB backend) |
| Auth | django-allauth (email-only + MFA) + django-axes |
| Static | WhiteNoise |
| Logging | structlog (JSON in prod, pretty in dev) |
| Deploy | Docker + Caddy on single VPS |
| Settings | Split: `base` / `local` / `production` / `test` |

## Quick start

```sh
cp .env.example .env          # edit DJANGO_SECRET_KEY at minimum
uv sync
uv run manage.py migrate
uv run manage.py createcachetable --database cache
uv run manage.py createsuperuser
uv run manage.py runserver
```

Visit http://127.0.0.1:8000/admin/

## Mise tasks

```sh
mise run server          # dev server
mise run worker          # background task worker
mise run migrate
mise run test
mise run lint
mise run typecheck
mise run collectstatic
```

## Production deploy

1. Build and push image:
   ```sh
   docker build --target prod -t ghcr.io/your-org/07-vps-sqlite-saas:latest .
   docker push ghcr.io/your-org/07-vps-sqlite-saas:latest
   ```

2. On the VPS, create `.env.prod` with all required vars (see `.env.example`), then:
   ```sh
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d --wait
   ```

3. Edit `Caddyfile` to replace `yourdomain.com` with your actual domain.

## Key environment variables

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | yes | 50-char random string |
| `DJANGO_ALLOWED_HOSTS` | prod | comma-separated hostnames |
| `DATABASE_URL` | prod | `sqlite:////data/db.sqlite3` |
| `EMAIL_URL` | prod | `smtp+tls://token:token@smtp.postmarkapp.com:587` |
| `DEFAULT_FROM_EMAIL` | prod | sender address |
| `SENTRY_DSN` | optional | Sentry error tracking |
| `LITESTREAM_BUCKET` | prod | S3 bucket name |
| `LITESTREAM_ACCESS_KEY_ID` | prod | S3 key |
| `LITESTREAM_SECRET_ACCESS_KEY` | prod | S3 secret |
| `LITESTREAM_ENDPOINT` | optional | For R2/MinIO/etc |

## Health endpoints

- `GET /healthz` → `ok` (liveness)
- `GET /readyz` → `ready` (DB connectivity check)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

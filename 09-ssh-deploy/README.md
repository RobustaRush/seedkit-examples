## Prompt

```
/seedkit

Project name: 09-ssh-deploy
Purpose: production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

Settings layout: split.
Database: PostgreSQL.
Local dev mode: docker-compose (web + db + redis).
Docker structure: override (one multi-stage `Dockerfile` with `dev`/`prod` targets, `docker-compose.yml` + `docker-compose.override.yml`).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: none.
Add-ons:
  - redis
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - analytics: Umami (self-hosted, env-driven website ID and host)
  - email: none (deliberately skip `references/email.md`; this project does not send transactional mail and the test verifies the skip path).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings
  - CSP via `django-csp`: yes
  - error reporting: Bugsink (self-hosted, sentry-sdk DSN)
  - GDPR: PII scrubbing in error reports, retention defaults, user data export/delete
  - CI: GitHub Actions test workflow
  - deploy: GitHub Actions deploy via SSH (rsync + remote `docker compose pull && up -d`)
  - database backups via `django-dbbackup`: yes (self-managed host — no native backup service)
  - production Dockerfile: single-stage (small enough; multi-stage not needed)

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 7 |
| Background tasks | django-tasks-rq (RQ backend) |
| Logging | structlog (JSON in prod / pretty in dev) |
| Analytics | Umami (self-hosted) |
| Error reporting | Bugsink (self-hosted, Sentry-compatible DSN) |
| Database backups | django-dbbackup → S3-compatible storage |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Local dev | docker-compose (web + worker + db + redis) |
| Production | GitHub Actions SSH deploy → VPS with Docker + Caddy |

## Local development

```sh
cp .env.example .env        # edit DJANGO_SECRET_KEY at minimum
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000/admin/

## Commands

```sh
# Run tests
docker compose exec web python -m pytest

# Lint
docker compose exec web ruff check .
docker compose exec web ruff format --check .

# Background worker (already running via docker compose)
docker compose logs -f worker

# Health checks
curl http://localhost:8000/healthz    # → ok
curl http://localhost:8000/readyz     # → ready

# GDPR
docker compose exec web python manage.py export_user_data <id>
docker compose exec web python manage.py delete_user <id> --yes
```

## Adding a dependency

```sh
uv add somepkg
docker compose build
docker compose up -d
```

## Production deploy

Set the following GitHub secrets in repo settings:
- `SSH_HOST` — VPS IP or hostname
- `SSH_USER` — SSH login user
- `SSH_KEY` — private key (the VPS must have the matching public key in `authorized_keys`)
- `GHCR_TOKEN` — PAT with `read:packages` (the VPS needs this to pull the image)

On the VPS, create `/srv/09-ssh-deploy/deploy/` and copy `deploy/.env.prod.example` → `deploy/.env.prod`, filling in all values.

Push to `main` to trigger a deploy.

## Database backups

Backups land in an S3-compatible bucket (set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DBBACKUP_BUCKET` in `.env.prod`).

```sh
# Run manually from the VPS
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml exec web python manage.py dbbackup --clean
```

Add a cron on the VPS:
```cron
17 3 * * * root cd /srv/09-ssh-deploy && docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml exec -T web python manage.py dbbackup --clean
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

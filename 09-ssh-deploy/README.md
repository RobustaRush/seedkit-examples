## Prompt

```
/seedkit

Project name: 09-ssh-deploy
Purpose: production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

Settings layout: split.
Database: PostgreSQL.
Postgres location: Postgres-in-Docker (`db` + `redis` services in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: mise.
Add-ons:
  - redis
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - analytics: Umami (self-hosted, env-driven website ID and host)
  - email: none (this project does not send transactional mail and the test verifies the skip path).
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
  - production Dockerfile: multi-stage — uv builder → `python:3.12-slim-bookworm` runtime

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

- **Django 6** · split settings (local / production / test)
- **PostgreSQL 17** (Docker in dev, VPS container in prod)
- **Redis 7** — cache (`/0`) + RQ task queue (`/3`)
- **Django Tasks + django-tasks-rq** — background tasks via RQ
- **structlog** — JSON in prod, pretty console in dev, per-request `request_id`
- **django-csp** — Content Security Policy in production
- **sentry-sdk** — Bugsink (self-hosted) error reporting
- **django-dbbackup** — daily DB backups to S3-compatible storage
- **Umami** (self-hosted) — cookieless analytics
- **Gunicorn** — WSGI server; **Caddy** — TLS + reverse proxy
- **Ruff** — lint + format; **pytest** — tests
- **mise** — task runner; **GitHub Actions** — CI + SSH deploy

## Quick start

```sh
mise trust && mise install   # installs Python 3.12 via mise
cp .env.example .env         # edit DJANGO_SECRET_KEY at minimum
docker compose up -d         # starts db (port 5433) + redis
mise run migrate
mise run dev
```

Open <http://localhost:8000/admin/>

## Common tasks

| Task | Command |
|---|---|
| Run dev server | `mise run dev` |
| Run migrations | `mise run migrate` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Background worker | `mise run worker` |
| Create superuser | `mise run superuser` |

Fallback (no mise): `uv run manage.py <command>`

## Health checks

- `GET /healthz` — liveness (process alive)
- `GET /readyz` — readiness (DB reachable)

## Deploy

Automated via GitHub Actions on push to `main`. Requires three repository secrets:

- `SSH_HOST` — VPS IP or hostname
- `SSH_USER` — SSH user on the VPS
- `SSH_KEY` — private key for SSH access
- `GHCR_TOKEN` — PAT with `read:packages` for the VPS to pull the image

### First-time VPS setup

```sh
ssh $SSH_USER@$SSH_HOST
mkdir -p /srv/09-ssh-deploy/deploy
cd /srv/09-ssh-deploy
cp deploy/.env.prod.example deploy/.env.prod
# edit deploy/.env.prod with real values
```

### Manual deploy

```sh
mise run deploy-migrate   # runs migrate in prod container
mise run deploy           # docker compose up -d
```

## Database backups

`django-dbbackup` dumps to an S3-compatible bucket daily. Configure in `deploy/.env.prod`:

```sh
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
DBBACKUP_BUCKET=
```

Manual backup: `docker compose exec -T web python manage.py dbbackup --clean`

## GDPR management commands

```sh
# Export all data for a user
uv run manage.py export_user_data <user_id>

# Permanently delete a user and all related data
uv run manage.py delete_user_data <user_id>
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

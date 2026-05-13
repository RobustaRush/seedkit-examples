## Prompt

```
/seedkit-slim

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

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 16 (Docker) |
| Cache / Queue | Redis 7 (Docker) |
| Background tasks | django-tasks-rq (RQ backend) |
| Logging | structlog + django-structlog (JSON/prod, pretty/dev, request_id) |
| Static files | WhiteNoise |
| Error reporting | Bugsink via sentry-sdk |
| CSP | django-csp 4.x |
| DB backups | django-dbbackup |
| Analytics | Umami (self-hosted, env-driven) |
| CI | GitHub Actions |
| Deploy | GitHub Actions → SSH → rsync → `docker compose pull && up -d` |

## Local development

```sh
# 1. Copy env
cp .env.example .env   # edit SECRET_KEY and DB/Redis creds if needed

# 2. Start DB + Redis
docker compose up -d --wait

# 3. Migrate and run
mise run migrate
mise run dev          # http://127.0.0.1:8000
mise run worker       # RQ worker (separate terminal)

# 4. Tests & lint
mise run test
mise run lint
```

## Key commands

```sh
uv run manage.py createsuperuser
uv run manage.py dbbackup
uv run manage.py export_user_data <user_id>    # GDPR Art. 20
uv run manage.py delete_user_data <user_id>    # GDPR Art. 17
```

## GDPR

- Error reports to Bugsink have PII stripped via `before_send` (no cookies, no auth headers, user reduced to ID).
- Session lifetime: 2 weeks (`SESSION_COOKIE_AGE`).
- `export_user_data` / `delete_user_data` management commands handle Art. 20 / Art. 17 requests.

## Deploy (GitHub Actions)

1. Push to `main` triggers `test.yml` (lint + pytest against real Postgres/Redis).
2. On success, `deploy.yml` builds the Docker image, pushes to GHCR, then SSH-deploys:
   - `rsync` the compose file to the server.
   - `docker compose -f docker-compose.prod.yml pull && up -d` on the remote host.

Required GitHub secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`.

## Umami analytics

Set `UMAMI_HOST` and `UMAMI_WEBSITE_ID` in the environment. The base template injects the script tag automatically when both values are present.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

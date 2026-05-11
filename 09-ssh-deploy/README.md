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
Add-ons:
  - redis
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`)
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
  - production Dockerfile: single-stage (small enough; multi-stage not needed)

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

- Python 3.12+ · Django 6 · PostgreSQL 17 · Redis 7
- django-tasks-rq (background tasks via RQ)
- structlog (JSON in prod / pretty in dev, per-request `request_id`)
- Umami analytics (self-hosted, env-driven)
- Bugsink error reporting (self-hosted, Sentry-compatible)
- django-csp Content Security Policy
- GitHub Actions: test CI + SSH deploy

## Local development

```sh
cp .env.example .env           # edit DJANGO_SECRET_KEY
docker compose up -d --build   # starts web + worker + db + redis (dev target)
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
# open http://localhost:8000/admin/
```

Adding a dependency:

```sh
uv add <package>
docker compose build web worker
docker compose up -d
```

## Testing

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Production deploy

1. Copy `deploy/.env.prod.example` → `deploy/.env.prod` on the server and fill in all values.
2. Set GitHub repository secrets: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN`.
3. Push to `main` — the deploy workflow builds the `prod` image, pushes to GHCR, SSH-es to the server, pulls, migrates, and brings the stack up.

Production stack (`deploy/docker-compose.prod.yml`): web + worker + db + redis + bugsink.

## Key endpoints

- `/admin/` — Django admin
- `/django-rq/` — RQ dashboard (admin-authenticated)
- `/healthz` — liveness (no DB check)
- `/readyz` — readiness (DB check)

## GDPR management commands

```sh
python manage.py export_user_data <user_id>   # JSON to stdout (Article 20)
python manage.py delete_user <user_id> --yes  # cascade delete + audit log (Article 17)
```

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
Task runner: mise.
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

- **Django 6** + PostgreSQL + Redis
- **Background tasks**: `django-tasks-rq` (Redis Queue backend)
- **Logging**: `structlog` — pretty console in dev, JSON in prod
- **Analytics**: Umami (self-hosted, cookieless)
- **Error reporting**: Bugsink (self-hosted, Sentry-protocol)
- **CI**: GitHub Actions — lint, test, deploy check
- **Deploy**: GitHub Actions → SSH → `docker compose` on VPS
- **Backups**: `django-dbbackup` to S3-compatible storage

## Local development

```sh
cp .env.example .env          # edit DATABASE_URL / REDIS_URL if not using docker-compose
mise trust && mise install    # or: uv sync

# Start the full stack (web + worker + db + redis):
docker compose up -d --wait

# Migrate and create a superuser:
mise run migrate
mise run superuser

# Open http://localhost:8000
```

## Task runner (mise)

| Task | Command |
|------|---------|
| `mise run dev` | Django dev server |
| `mise run migrate` | Apply migrations |
| `mise run makemigrations` | Create migrations |
| `mise run test` | Run pytest |
| `mise run lint` | Ruff check |
| `mise run fmt` | Ruff format |
| `mise run worker` | Start RQ worker |
| `mise run superuser` | Create superuser |
| `mise run collectstatic` | Collect static files |

Fallback without mise: `uv run manage.py <command>`

## Testing

```sh
mise run test
# or:
uv run pytest
uv run pytest --cov
```

## Deploy

Copy `deploy/.env.prod.example` to `deploy/.env.prod` on the server and fill in all values.

Set these secrets in GitHub repo settings:
- `SSH_HOST` — VPS hostname or IP
- `SSH_USER` — SSH username
- `SSH_KEY` — private SSH key (the server must have the public key)
- `GHCR_TOKEN` — GitHub PAT with `read:packages` scope (for the server to pull images)

Push to `main` to trigger the deploy workflow. It builds and pushes the image to GHCR, then SSHs into the server and runs:

```sh
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web uv run manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

## Database backups

Backups run daily on the server via cron. Add to `/etc/cron.d/dbbackup`:

```cron
17 3 * * * root cd /srv/09-ssh-deploy && docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml exec -T web python manage.py dbbackup --clean
```

Requires `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `DBBACKUP_BUCKET` in `deploy/.env.prod`.

## Health checks

- `/healthz` — liveness (process alive, no external checks)
- `/readyz` — readiness (DB reachable)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

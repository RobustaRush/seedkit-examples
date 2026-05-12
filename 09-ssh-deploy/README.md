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
  - production Dockerfile: multi-stage (per `references/docker.md`) — uv builder → `python:3.12-slim-bookworm` runtime

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production Django app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

- **Django 6** · PostgreSQL · Redis
- **Background tasks**: Django Tasks + RQ (`django-tasks-rq`)
- **Logging**: structlog (pretty in dev, JSON in prod, request-scoped `request_id`)
- **Analytics**: Umami (self-hosted, env-driven)
- **Error reporting**: Bugsink (self-hosted, sentry-sdk DSN)
- **Security**: Django hardening + Content Security Policy (`django-csp`)
- **GDPR**: PII scrubbing in error reports; `export_user_data` / `delete_user_data` management commands
- **Database backups**: `django-dbbackup` to S3-compatible storage
- **CI**: GitHub Actions test workflow
- **Deploy**: GitHub Actions → SSH → rsync + `docker compose pull && up -d`

## Setup

```sh
mise trust && mise install   # pins Python 3.12 via mise
mise run install             # uv sync
cp .env.example .env         # then set DJANGO_SECRET_KEY
docker compose up -d         # starts db + redis
mise run migrate
mise run superuser
mise run dev
```

## Commands

| Task | Command |
|------|---------|
| `mise run dev` | Start development server |
| `mise run migrate` | Apply database migrations |
| `mise run test` | Run test suite |
| `mise run lint` | Ruff lint check |
| `mise run fmt` | Ruff format |
| `mise run worker` | Start RQ worker |
| `mise run superuser` | Create superuser |
| `mise run deploy` | Migrate + `docker compose up -d` on prod |

Fallback (no mise): `uv run manage.py <command>`.

## Health checks

- `GET /healthz` → `ok` (liveness — no external checks)
- `GET /readyz` → `ready` (readiness — DB ping)

## Deploy

Prerequisites: set repo secrets `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN`.

On the VPS:
```sh
mkdir -p /srv/09-ssh-deploy
cd /srv/09-ssh-deploy
cp deploy/.env.prod.example deploy/.env.prod
# fill in all values in deploy/.env.prod
```

Every push to `main` triggers `.github/workflows/deploy.yml`:
1. Builds and pushes Docker image to GHCR
2. SSHes to VPS, pulls new image, runs `manage.py migrate`, then `docker compose up -d`
3. Waits for the container healthcheck to flip healthy

Manual deploy:
```sh
ssh user@vps
cd /srv/09-ssh-deploy
export GITHUB_REPOSITORY=owner/repo
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

## Database backups

Backups run via cron on the VPS host:
```cron
17 3 * * * django docker compose exec -T web python manage.py dbbackup --clean
27 3 * * * django docker compose exec -T web python manage.py mediabackup --clean
```

Requires `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DBBACKUP_BUCKET` in `deploy/.env.prod`.

## GDPR

```sh
uv run manage.py export_user_data <user_id>
uv run manage.py delete_user_data <user_id>
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

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

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 17 |
| Cache / Task queue | Redis 7 |
| Background tasks | Django Tasks + `django-tasks-rq` |
| Structured logging | structlog + django-structlog (JSON in prod, pretty in dev) |
| Analytics | Umami (self-hosted, cookieless) |
| Error reporting | Bugsink (self-hosted, Sentry protocol) |
| Database backups | django-dbbackup → S3-compatible storage |
| Static files | `collectstatic` into `staticfiles/` (WhiteNoise can be added) |
| Reverse proxy | Caddy (TLS, health probe) |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| Task runner | mise |
| Deploy | GitHub Actions → SSH → `docker compose` on VPS |

## Local development

```sh
cp .env.example .env        # then edit DATABASE_URL / REDIS_URL if running outside compose
mise trust && mise install   # installs Python 3.12 + uv deps; or: uv sync
```

Start the full stack (web + worker + db + redis):

```sh
docker compose up -d --wait
mise run migrate
```

Open <http://localhost:8000/admin/>.

## Task runner (mise)

| Task | Command |
|---|---|
| `mise run dev` | `uv run manage.py runserver` |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run makemigrations` | `uv run manage.py makemigrations` |
| `mise run shell` | `uv run manage.py shell` |
| `mise run superuser` | `uv run manage.py createsuperuser` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run worker` | `uv run manage.py rqworker default` |
| `mise run deploy-migrate` | one-shot migrate against prod compose |
| `mise run deploy` | migrate + `docker compose up -d` against prod |

Without mise: use `uv run manage.py <cmd>` directly.

## Health checks

| Endpoint | Purpose |
|---|---|
| `/healthz` | Liveness — process alive, no external checks |
| `/readyz` | Readiness — DB reachable |

## Background tasks (jobs app)

The `jobs` app registers a sample `@task` (`send_welcome_email`). Add domain tasks to `jobs/tasks.py`. Enqueue with:

```python
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue(user_id=42)
```

Worker logs are visible via `docker compose logs worker`.

## Analytics (Umami)

Set `ANALYTICS_ID` and `ANALYTICS_HOST` in `.env.prod`. The `_analytics.html` template is included in your base template. Tracking is disabled in dev (gated on `not DEBUG`).

## Error reporting (Bugsink)

Set `SENTRY_DSN` in `.env.prod`. Bugsink runs as a service in `deploy/docker-compose.prod.yml`. Configure a project at `https://bugsink.example.com` to get the DSN.

## Database backups (django-dbbackup)

Configure `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `DBBACKUP_BUCKET` in `.env.prod`.

Run backups from the VPS cron:

```cron
17 3 * * * django docker compose exec -T web python manage.py dbbackup --clean
```

Restore:

```sh
docker compose exec -T web python manage.py dbrestore --database=default
```

## GDPR

- Sentry SDK runs with `send_default_pii=False` and strips `Authorization` / `Cookie` headers from error reports.
- Session cookies set with `Secure` and `SameSite=Lax`.
- User data export/delete: implement `manage.py export_user_data` and `manage.py delete_user` commands per your data model.

## Deploy

### First-time VPS setup

1. SSH to the VPS, create `/srv/09-ssh-deploy/`.
2. Copy `deploy/` directory and `deploy/.env.prod.example` → `deploy/.env.prod`, fill in all values.
3. Add the `GHCR_TOKEN` PAT (with `read:packages`) to repo secrets alongside `SSH_HOST`, `SSH_USER`, `SSH_KEY`.

### CI/CD

Every push to `main` triggers `.github/workflows/deploy.yml`:

1. Builds and pushes the `prod` Docker image to GHCR.
2. SSH to the VPS, pulls the new image, runs `manage.py migrate`, restarts services.
3. Waits for the container healthcheck to flip to `healthy`.

### Manual deploy

```sh
mise run deploy
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

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

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 7 |
| Background tasks | django-tasks-rq (RQ backend) |
| Logging | structlog (pretty dev / JSON prod) |
| Analytics | Umami (self-hosted) |
| Error tracking | Bugsink (self-hosted, sentry-protocol) |
| Web server | gunicorn |
| Lint | Ruff |
| Tests | pytest + pytest-django |
| CI | GitHub Actions |
| Deploy | GitHub Actions → SSH → rsync + docker compose |

## Local development

```sh
cp .env.example .env            # edit DJANGO_SECRET_KEY
docker compose up -d --wait     # starts web, worker, db, redis
docker compose exec -T web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

Add a dependency:

```sh
uv add somepkg                  # updates pyproject.toml + uv.lock
docker compose build web worker
docker compose up -d
```

## Key URLs

| URL | Purpose |
|---|---|
| `/admin/` | Django admin |
| `/healthz` | Liveness probe (no DB check) |
| `/readyz` | Readiness probe (DB check) |

## Tests

```sh
uv run pytest
```

## Lint

```sh
uv run ruff check .
uv run ruff format .
```

## Production deploy

GitHub Actions runs `.github/workflows/deploy.yml` on every push to `main`:

1. Builds the `prod` Docker target and pushes to `ghcr.io/<owner>/<repo>:latest`.
2. SSH into the server, pulls the new image, runs `migrate`, restarts services.

### Required secrets (GitHub repo settings)

| Secret | Value |
|---|---|
| `SSH_HOST` | Server IP or hostname |
| `SSH_USER` | Deploy user |
| `SSH_KEY` | Private key (matching the server's `~/.ssh/authorized_keys`) |
| `GHCR_TOKEN` | PAT with `read:packages` (used by the server to pull private images) |

### First deploy

```sh
# On the server:
mkdir -p /srv/09-ssh-deploy/deploy
cp deploy/.env.prod.example /srv/09-ssh-deploy/deploy/.env.prod
# edit /srv/09-ssh-deploy/deploy/.env.prod with real secrets
```

Then push to `main` — GitHub Actions handles the rest.

## GDPR management commands

```sh
python manage.py export_user_data <user_id> > data.json   # Article 20
python manage.py delete_user <user_id>                     # Article 17
```

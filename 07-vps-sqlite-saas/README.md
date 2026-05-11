## Prompt

```
/seedkit

Project name: 07-vps-sqlite-saas
Purpose: production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

Settings layout: split.
Database: SQLite.
Local dev mode: docker-compose (full stack: web only — no db / redis services).
Docker structure: simple (separate `Dockerfile.dev` for dev, single-stage production `Dockerfile`).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: yes.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login + mandatory verification).
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: none.
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
  - database backups: Litestream replication to S3-compatible storage (the SQLite production path in `references/database.md`); do not use `django-dbbackup`
  - production Dockerfile: single-stage; install the Litestream `.deb`, ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
Skip GDPR for this case.

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `Caddyfile`, `litestream.yml`, `entrypoint.sh`, `.github/workflows/test.yml`. Do not actually push to a remote VPS — just verify all artifacts are present and `docker build .` succeeds.
```

---

# 07-vps-sqlite-saas

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | SQLite (WAL mode, `/data/site.sqlite3`) |
| Cache | SQLite (`/data/cache.sqlite3` + `CacheRouter`) |
| Background tasks | `django-tasks-db` (DB backend, `db_worker`) |
| Auth | `django-allauth` (email login, mandatory verification in prod) |
| 2FA | `allauth.mfa` (TOTP + recovery codes) |
| Brute-force protection | `django-axes` |
| Static files | WhiteNoise (manifest storage in prod) |
| Media files | Docker volume, served by Caddy |
| Structured logging | `structlog` + `django-structlog` (JSON in prod, pretty in dev) |
| Error reporting | Sentry SDK |
| CSP | `django-csp` (production only) |
| DB replication | Litestream → S3-compatible storage |
| Server | gunicorn |
| Reverse proxy | Caddy 2 |

## Local development (Docker)

```sh
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY to something random

docker compose up -d --wait
docker compose exec -T web python manage.py migrate
docker compose exec -T web python manage.py createcachetable --database cache
docker compose exec web python manage.py createsuperuser
```

Open <http://localhost:8000/admin/>.

### Adding a dependency

```sh
uv add somepkg
docker compose build web
docker compose up -d
```

## Testing

```sh
uv run pytest
uv run pytest --cov
```

## Lint / format

```sh
uv run ruff check .
uv run ruff format .
```

## Type check

```sh
uv run pyright
```

## Pre-commit hooks

```sh
uv run pre-commit install
```

## Health checks

- `GET /healthz` → `ok` (liveness — process alive)
- `GET /readyz` → `ready` (readiness — DB reachable)

## Background tasks

```python
from jobs.tasks import example_task
example_task.enqueue("hello")
```

Run a worker:

```sh
docker compose exec web python manage.py db_worker
```

## Production deploy (VPS)

1. Build and push the image:
   ```sh
   docker build -t ghcr.io/robustarush/07-vps-sqlite-saas:latest .
   docker push ghcr.io/robustarush/07-vps-sqlite-saas:latest
   ```

2. On the VPS, create `.env.prod` from `.env.example` and fill in production values:
   ```sh
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<strong-random-key>
   DJANGO_ALLOWED_HOSTS=example.com
   DATABASE_URL=sqlite:////data/site.sqlite3
   EMAIL_URL=smtp+tls://<token>:<token>@smtp.postmarkapp.com:587
   DEFAULT_FROM_EMAIL=no-reply@example.com
   DJANGO_BEHIND_PROXY=True
   DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com
   SENTRY_DSN=<dsn>
   S3_ENDPOINT=https://...
   S3_BUCKET=myproject
   S3_ACCESS_KEY_ID=...
   S3_SECRET_ACCESS_KEY=...
   ```

3. Edit `Caddyfile` — replace `example.com` with your domain.

4. Start:
   ```sh
   docker compose -f docker-compose.prod.yml up -d
   ```

> **Note**: NTP must be configured on the server — TOTP 2FA fails if clock skew exceeds 30 s.

## Environment variables reference

| Variable | Default (dev) | Required in prod |
|---|---|---|
| `DJANGO_SECRET_KEY` | insecure default | yes |
| `DJANGO_DEBUG` | `True` | no (omit or `False`) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | yes |
| `DATABASE_URL` | `sqlite:///BASE_DIR/db.sqlite3` | yes |
| `EMAIL_URL` | `consolemail://` | yes |
| `DEFAULT_FROM_EMAIL` | `webmaster@localhost` | yes |
| `SERVER_EMAIL` | same as `DEFAULT_FROM_EMAIL` | no |
| `DJANGO_ADMINS` | empty | no |
| `DJANGO_SITE_DOMAIN` | `example.com` | yes (for TOTP issuer) |
| `DJANGO_BEHIND_PROXY` | `False` | yes (behind Caddy) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | yes |
| `SENTRY_DSN` | empty | no |
| `S3_ENDPOINT` | — | yes (Litestream) |
| `S3_BUCKET` | — | yes (Litestream) |
| `S3_ACCESS_KEY_ID` | — | yes (Litestream) |
| `S3_SECRET_ACCESS_KEY` | — | yes (Litestream) |

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

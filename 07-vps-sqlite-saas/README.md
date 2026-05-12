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
  - database backups: Litestream replication to S3-compatible storage (the SQLite production path in `references/database.md`); do not use `django-dbbackup`
  - production Dockerfile: single-stage; install the Litestream `.deb`, ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
Skip GDPR for this case.

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `Caddyfile`, `litestream.yml`, `entrypoint.sh`, `.github/workflows/test.yml`. Do not actually push to a remote VPS — just verify all artifacts are present and `docker build .` succeeds.
```

---

# 07-vps-sqlite-saas

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

## Stack

- **Django 6** · split settings (base / local / production / test)
- **Auth** · django-allauth (email login + mandatory verification in prod) · django-axes (brute-force lockout) · allauth.mfa (TOTP 2FA)
- **Database** · SQLite on a persistent Docker volume · WAL mode in production
- **Cache** · `cache.sqlite3` (separate file) + `DatabaseCache` + `CacheRouter`
- **Tasks** · Django Tasks with `django-tasks-db` backend · `jobs` app with sample `@task`
- **Static** · WhiteNoise (compressed + hashed filenames in prod) · media served via Caddy
- **Email** · console backend in dev · SMTP (Postmark) in prod
- **Logging** · structlog · pretty console in dev / JSON in prod · `request_id` via `django-structlog`
- **Error reporting** · Sentry SaaS (set `SENTRY_DSN`)
- **Security** · HSTS, secure cookies, CSP (`django-csp`), `X-Frame-Options`
- **Backups** · Litestream replicates every WAL frame to S3-compatible storage
- **CI** · GitHub Actions (ruff, pyright, pytest)
- **Deploy** · VPS with Docker + Caddy · `deploy/docker-compose.prod.yml`

## Quick start

```sh
cp .env.example .env
# edit .env: set DJANGO_SECRET_KEY to a real random value

mise run dev        # or: uv run manage.py runserver
```

### Docker (local)

```sh
docker compose up -d --build
docker compose exec web uv run manage.py migrate
docker compose exec web uv run manage.py createcachetable --database cache
docker compose exec web uv run manage.py createsuperuser
# open http://localhost:8000/admin/
```

## Task runner (mise)

```sh
mise run install          # uv sync
mise run dev              # runserver
mise run migrate          # manage.py migrate
mise run makemigrations   # manage.py makemigrations
mise run test             # pytest
mise run lint             # ruff check .
mise run fmt              # ruff format .
mise run typecheck        # pyright
mise run worker           # manage.py db_worker
mise run collectstatic    # manage.py collectstatic --noinput
```

First-time: `mise trust && mise install`

Fallback without mise: `uv run manage.py <cmd>`

## Tests

```sh
uv run pytest
uv run pytest --cov       # with coverage
```

## Deploy (VPS)

Requires `.env.prod` on the server. Litestream restores the DB from S3 on first boot.

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d
```

The `entrypoint.sh` inside the image handles restore → migrate → `createcachetable` → `litestream replicate -exec gunicorn`.

## Production env vars

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | yes | 50-char random string |
| `DJANGO_ALLOWED_HOSTS` | yes | comma-separated domains |
| `DATABASE_URL` | yes | `sqlite:////data/site.sqlite3` |
| `CACHE_DB_PATH` | yes | `/data/cache.sqlite3` |
| `EMAIL_URL` | yes | `smtp+tls://<token>:<token>@smtp.postmarkapp.com:587` |
| `DEFAULT_FROM_EMAIL` | yes | sender address |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | yes | `https://example.com` |
| `DJANGO_BEHIND_PROXY` | yes | `True` (Caddy terminates TLS) |
| `DJANGO_SITE_DOMAIN` | yes | shown in TOTP QR code |
| `S3_ENDPOINT` / `S3_BUCKET` / `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | yes | Litestream replication target |
| `SENTRY_DSN` | optional | error reporting |

## Health endpoints

- `GET /healthz` → `ok` (process alive)
- `GET /readyz` → `ready` (DB reachable) or `db down` (503)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

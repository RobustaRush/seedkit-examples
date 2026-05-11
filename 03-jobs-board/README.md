## Prompt

```
/seedkit

Project name: 03-jobs-board
Purpose: job board with background email notifications and a daily digest.

Settings layout: single file.
Database: PostgreSQL.
Local dev mode: uv on host. Postgres location: run only Postgres in Docker, Django runs on the host (publish 5432 to localhost).
Lint with Ruff: no.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): yes.
Custom user model: no.
Auth add-on: `django-mail-auth` (passwordless magic-link).
Structured logging: no.
Add-ons:
  - redis (for Celery)
  - tasks: Celery, with periodic tasks (Celery Beat)
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.

Production setup: skip.

Ship a `docker-compose.yml` with `db` and `redis` services only. Run the foundation, start the containers, run migrate + createsuperuser, and define one trivial Celery task plus one Beat-scheduled task to prove autodiscovery works.
```

---

# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack

- **Django** with single `config/settings.py`
- **PostgreSQL** (Docker) + **uv** on host
- **django-mail-auth** — passwordless magic-link login
- **Celery** + **Celery Beat** — background tasks and scheduled daily digest
- **Redis** — Celery broker and Django cache
- **django-redis** — shared cache backend
- **i18n** — gettext, LocaleMiddleware, `locale/` directory
- **Health checks** — `/healthz` (liveness) and `/readyz` (readiness)

## Local dev setup

```sh
cp .env.example .env
# Set a real secret key:
python -c "import secrets; print('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50))"
# paste the line into .env

docker compose up -d --wait        # starts db + redis
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://localhost:8000/admin/>.

## Key commands

```sh
uv run manage.py migrate
uv run manage.py test
uv run manage.py makemessages -l en
uv run manage.py compilemessages

# Background worker (separate terminal):
uv run celery -A config worker -l info

# Beat scheduler (separate terminal):
uv run celery -A config beat -l info
```

## Celery tasks

- `jobs.tasks.send_notification_email(user_id, subject, message)` — one-off email notification
- `jobs.tasks.send_daily_digest()` — scheduled daily at 08:00 UTC via Beat

## Endpoints

| Path | Description |
|------|-------------|
| `/` | Redirects to `/admin/` |
| `/admin/` | Django admin (magic-link login) |
| `/accounts/login/` | Magic-link login |
| `/healthz` | Liveness probe — returns `ok` |
| `/readyz` | Readiness probe — checks DB, returns `ready` |

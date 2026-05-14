## Prompt

```
/seedkit

Project name: 02-shop
Purpose: small e-commerce site with admin and SMTP transactional email.

Settings layout: split (`config/settings/base.py`, `local.py`, `production.py`).
Database: PostgreSQL.
Postgres location: on the host (use `createdb` for the project DB).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login, mandatory email verification, no social providers).
Structured logging: no.
Task runner: mise.
Add-ons:
  - storage: WhiteNoise for static files (no media volume yet)
  - email: SMTP (console backend in local, SMTP in production)
  - CORS: no.
  - REST API: none.
  - Frontend: `tailwind-cli` (custom 404/403/500 templates: yes; DaisyUI: yes). Also add a `pages` app with an `IndexView(TemplateView)` wired at `/`. Its `index.html` must include `text-blue-600` and `text-4xl` (utility check) and a `<button class="btn btn-primary">` (DaisyUI check) — concrete grep targets for the integration tests below.
  - Auth hardening: `django-axes` (yes), 2FA (no).
  - Billing: `stripe` raw SDK.
  - Health check endpoints: yes.
  - `robots.txt`: yes.
  - `django-extensions`: no.

Production setup: VPS (Docker + Caddy). Use a multi-stage `Dockerfile` (uv builder → `python:3.12-slim-bookworm` runtime).

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

# 02-shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- Django 6 + PostgreSQL + django-environ
- Auth: django-allauth (email login, mandatory verification in prod) + django-axes (brute-force lockout)
- Frontend: Tailwind CSS 4 + DaisyUI via django-tailwind-cli (no Node)
- Static files: WhiteNoise (CompressedManifestStaticFilesStorage in prod)
- Billing: Stripe raw SDK
- Email: console in dev, SMTP in prod via `EMAIL_URL`
- Type checking: pyright + django-stubs
- Lint: Ruff
- Tests: pytest + pytest-django
- Task runner: mise
- Deploy: VPS (Docker + Caddy)

## Setup

```sh
cp .env.example .env   # then fill in DJANGO_SECRET_KEY and DATABASE_URL
mise install           # installs Python 3.12 via mise
mise run install       # uv sync
createdb shop_db
mise run migrate
```

## Dev

```sh
mise run dev           # runserver + tailwind watcher
mise run superuser     # create admin user
```

## Tasks

| Task | Command |
|---|---|
| `mise run install` | `uv sync` |
| `mise run dev` | `uv run manage.py tailwind runserver` |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run makemigrations` | `uv run manage.py makemigrations` |
| `mise run shell` | `uv run manage.py shell` |
| `mise run superuser` | `uv run manage.py createsuperuser` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run tailwind` | `uv run manage.py tailwind build` |
| `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |
| `mise run deploy` | migrate + `docker compose … up -d` |

## Deploy

```sh
ssh user@vps
cd /srv/02-shop
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose -f deploy/docker-compose.prod.yml up -d
```

Copy `.env.example` to `.env.prod` on the VPS and fill in production values:
- `DJANGO_SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DATABASE_URL` — points at the `db` service: `postgres://postgres:<password>@db:5432/shop_db`
- `EMAIL_URL` — SMTP URL, e.g. `smtp+tls://apikey:<key>@smtp.sendgrid.net:587`
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `DJANGO_ALLOWED_HOSTS` — your domain name

For local Stripe webhook testing: `stripe listen --forward-to localhost:8000/billing/webhook/`

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

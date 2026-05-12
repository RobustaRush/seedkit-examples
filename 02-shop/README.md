## Prompt

```
/seedkit

Project name: 02-shop
Purpose: small e-commerce site with admin and SMTP transactional email.

Settings layout: split (`config/settings/base.py`, `local.py`, `production.py`).
Database: PostgreSQL.
Local dev mode: uv on host. Postgres location: on the host (use `createdb` for the project DB).
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

Production setup: VPS (Docker + Caddy). Dockerfile structure: simple (separate `Dockerfile.dev` + production `Dockerfile`). Use single-stage prod Dockerfile.

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

# shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (psycopg3) |
| Auth | django-allauth (email login, mandatory verification in prod) |
| Auth hardening | django-axes (brute-force lockout) |
| Static files | WhiteNoise (CompressedManifest in prod) |
| Frontend | Tailwind CSS 4 via tailwind-cli + DaisyUI |
| Email | Console (dev) · SMTP (prod) |
| Billing | Stripe raw SDK |
| Task runner | mise |
| Linter | Ruff |
| Tests | pytest + pytest-django |
| Type check | pyright + django-stubs |
| Production | Gunicorn + Docker + Caddy |

## Setup

```sh
mise trust && mise install   # installs Python 3.12
mise run install             # uv sync
cp .env.example .env         # fill in DJANGO_SECRET_KEY + DATABASE_URL
createdb shop_db
mise run migrate
mise run superuser
```

## Commands

| Task | What it does |
|---|---|
| `mise run dev` | Tailwind watch + runserver |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run makemigrations` | `uv run manage.py makemigrations` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run tailwind` | One-off production CSS build |
| `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |
| `mise run superuser` | `uv run manage.py createsuperuser` |

Fallback without mise: `uv run manage.py <cmd>`.

## Environment variables

See `.env.example` for the full list. Key vars:

| Variable | Required in prod | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | yes | Use `secrets.token_urlsafe(50)` |
| `DJANGO_DEBUG` | no | Unset = `False` |
| `DJANGO_ALLOWED_HOSTS` | yes | Comma-separated |
| `DATABASE_URL` | yes | `postgres://user:pass@host:5432/dbname` |
| `EMAIL_URL` | yes | `smtp+tls://user:pass@host:587` |
| `DEFAULT_FROM_EMAIL` | yes | Sender address |
| `STRIPE_PUBLISHABLE_KEY` | yes | |
| `STRIPE_SECRET_KEY` | yes | |
| `STRIPE_WEBHOOK_SECRET` | yes | |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | yes | e.g. `https://shop.example.com` |

## Stripe webhooks

Register `https://yourdomain.com/billing/webhook/` in Stripe Dashboard → Developers → Webhooks.

Local dev:

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
```

Use the printed `whsec_...` as `STRIPE_WEBHOOK_SECRET` in `.env`.

## Deploy (VPS)

```sh
ssh user@vps
cd /srv/shop
git pull
docker compose -f deploy/docker-compose.prod.yml pull
mise run deploy-migrate
mise run deploy
```

Or without mise:

```sh
docker compose -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose -f deploy/docker-compose.prod.yml up -d
```

Update `deploy/Caddyfile` with the real domain before first deploy.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

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

Production setup: VPS (Docker + Caddy). Use the multi-stage `Dockerfile` from `references/docker.md` (uv builder → `python:3.12-slim-bookworm` runtime).

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

# 02-shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- **Django 6** + PostgreSQL
- **Auth**: django-allauth (email login, email verification) + django-axes (brute-force protection)
- **Frontend**: Tailwind CSS v4 + DaisyUI via django-tailwind-cli (no Node.js)
- **Billing**: Stripe raw SDK
- **Static files**: WhiteNoise (CompressedManifestStaticFilesStorage in production)
- **Email**: console backend in dev, SMTP in production
- **Health checks**: `/healthz` (liveness) + `/readyz` (readiness)
- **Deploy**: VPS with Docker + Caddy

## Quick start

```sh
# Install dependencies
mise run install       # or: uv sync

# Create DB (host Postgres)
createdb shop_db

# Copy and configure env
cp .env.example .env  # then edit .env with real values

# Migrate and create superuser
mise run migrate
mise run superuser

# Build Tailwind CSS
uv run manage.py tailwind build

# Run dev server (with Tailwind watcher)
mise run dev
```

## Key commands

| Task | Command |
|---|---|
| Dev server | `mise run dev` |
| Migrate | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Collect static | `mise run collectstatic` |
| Shell | `mise run shell` |

Without mise: `uv run manage.py <command>`

## Environment variables

See `.env.example` for all variables. Key ones:

- `DJANGO_SECRET_KEY` — required in production
- `DATABASE_URL` — Postgres URL
- `EMAIL_URL` — `consolemail://` in dev, `smtp+tls://...` in production
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

## Production deploy

```sh
ssh user@vps
cd /srv/02-shop
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose -f deploy/docker-compose.prod.yml up -d
```

Update `deploy/Caddyfile` with your real domain before first deploy.

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

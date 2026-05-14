## Prompt

```
/seedkit-slim

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

Small e-commerce site with Django admin and SMTP transactional email.

## Stack

| Layer | Choice |
|---|---|
| Python | 3.12 |
| Framework | Django 5.x |
| Database | PostgreSQL (psycopg 3) |
| Auth | django-allauth (email login, mandatory verification) |
| Auth hardening | django-axes (brute-force lockout) |
| Static files | WhiteNoise |
| Frontend | Tailwind CSS v4 + DaisyUI |
| Billing | Stripe SDK |
| Task runner | mise |
| Linter | Ruff |
| Type checker | pyright + django-stubs |
| Tests | pytest + pytest-django |
| Production | Docker (multi-stage) + Caddy |

## Setup

```sh
# Create DB
createdb shop_db

# Copy env
cp .env.example .env
# Edit .env with your values

# Install Python deps
uv sync

# Install Node deps (Tailwind + DaisyUI)
npm install

# Build CSS
uv run manage.py tailwind build

# Migrate
uv run manage.py migrate

# Create superuser
uv run manage.py createsuperuser

# Run dev server
uv run manage.py runserver
```

## Key commands (via mise)

```sh
mise run server          # dev server
mise run tailwind        # build CSS
mise run tailwind-watch  # watch CSS
mise run migrate         # apply migrations
mise run test            # run tests
mise run lint            # ruff check
mise run typecheck       # pyright
mise run collectstatic   # collect static files
```

## Settings

| File | Purpose |
|---|---|
| `config/settings/base.py` | Shared settings |
| `config/settings/local.py` | Local dev (console email, DEBUG=True) |
| `config/settings/production.py` | Production (SMTP, security headers, SSL) |

Environment variables read via `django-environ` from `.env` (dev) or the host environment (production).

## Production Deploy

Build and push the Docker image, then run with these env vars:

```
DJANGO_SECRET_KEY=<strong-secret>
DJANGO_ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/shop_db
EMAIL_URL=smtp://user:pass@smtp.host:587
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
DOMAIN=yourdomain.com
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

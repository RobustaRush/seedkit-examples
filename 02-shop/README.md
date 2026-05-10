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

Production setup: skip.

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

# 02-shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- Django 6.x, Python 3.12+
- PostgreSQL via `psycopg[binary]` + `django-environ`
- Split settings: `config/settings/{base,local,production}.py`
- Custom `users.User` (email login, no username)
- `django-allauth` — email signup/login, mandatory email verification in production
- `django-axes` — brute-force lockout (5 failures → 1 hr cooloff)
- WhiteNoise — static file serving (production only)
- `django-tailwind-cli` + DaisyUI — CSS build, no Node required
- Stripe raw SDK — Checkout session, Customer Portal, webhook handler
- Health checks: `/healthz`, `/readyz`
- `robots.txt`
- Ruff lint/format, pytest + pytest-django, pyright + django-stubs

## Setup

```sh
cp .env.example .env
# edit .env: set DJANGO_SECRET_KEY to a real value

createdb shop_db

uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py tailwind build
uv run manage.py runserver
```

## Key commands

```sh
uv run manage.py tailwind runserver   # dev: watch + runserver
uv run manage.py migrate
uv run pytest
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Environment variables

See `.env.example` for the full list. Required in production:
- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `EMAIL_URL`
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

## Stripe local dev

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
# use the printed whsec_... as STRIPE_WEBHOOK_SECRET in .env
```

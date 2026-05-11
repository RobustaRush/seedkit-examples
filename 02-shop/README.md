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

Production setup: skip.

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

# 02-shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- **Django** — web framework
- **PostgreSQL** — database (psycopg3)
- **django-allauth** — email login with mandatory verification in production
- **django-axes** — brute-force lockout
- **Tailwind CSS + DaisyUI** — frontend (standalone CLI, no Node)
- **WhiteNoise** — static file serving in production
- **Stripe** — payments (raw SDK)
- **Ruff** — linting + formatting
- **pytest + pytest-django** — test runner
- **pyright + django-stubs** — type checking
- **mise** — task runner

## Setup

```sh
cp .env.example .env
# Edit .env: set DJANGO_SECRET_KEY, DATABASE_URL
createdb shop_db
mise run install
mise run migrate
mise run superuser
```

## Commands

```sh
mise run dev          # uv run manage.py tailwind runserver
mise run migrate      # uv run manage.py migrate
mise run test         # uv run pytest
mise run lint         # uv run ruff check .
mise run fmt          # uv run ruff format .
mise run typecheck    # uv run pyright
mise run collectstatic
```

Without mise: `uv run manage.py <cmd>`.

## Environment variables

See `.env.example` for the full list. Key vars:

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | yes | Django secret key |
| `DJANGO_DEBUG` | no | `True` for local dev |
| `DJANGO_ALLOWED_HOSTS` | prod | Comma-separated allowed hosts |
| `DATABASE_URL` | yes | Postgres connection URL |
| `EMAIL_URL` | yes | `consolemail://` locally, `smtp+tls://...` in production |
| `STRIPE_PUBLISHABLE_KEY` | billing | Stripe publishable key |
| `STRIPE_SECRET_KEY` | billing | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | billing | Stripe webhook signing secret |

## Stripe local dev

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
# Use the printed whsec_... as STRIPE_WEBHOOK_SECRET in .env
```

## Endpoints

- `/` — index page
- `/admin/` — Django admin
- `/accounts/` — allauth auth flows (login, signup, password reset)
- `/healthz` — liveness probe (text `ok`)
- `/readyz` — readiness probe (text `ready`, checks DB)
- `/robots.txt` — crawler policy
- `/billing/checkout/` — Stripe Checkout session
- `/billing/portal/` — Stripe Customer Portal
- `/billing/webhook/` — Stripe webhook receiver

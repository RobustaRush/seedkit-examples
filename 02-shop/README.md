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

- **Django** with split settings (`base` / `local` / `production`)
- **PostgreSQL** via `psycopg[binary]` + `django-environ` DATABASE_URL
- **Custom user model** — email-as-username (`users.User`)
- **django-allauth** — email login, mandatory email verification in production
- **django-axes** — brute-force lockout (5 failures / 1 hour cooloff)
- **WhiteNoise** — static files
- **django-tailwind-cli** + **DaisyUI** — CSS, no Node.js
- **Stripe** raw SDK — checkout, customer portal, webhook
- **pytest** + **pytest-django** — test runner
- **Ruff** — lint + format
- **pyright** + **django-stubs** — type checking

## Local setup

```sh
createdb shop_db
cp .env.example .env
# edit .env — set DJANGO_SECRET_KEY to something random
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py tailwind build
uv run manage.py runserver
```

Or use the watcher (rebuilds CSS on template changes):

```sh
uv run manage.py tailwind runserver
```

## Commands

| Command | Purpose |
|---|---|
| `uv run manage.py migrate` | Apply DB migrations |
| `uv run manage.py tailwind build` | Build production CSS |
| `uv run manage.py tailwind runserver` | Dev server + CSS watcher |
| `uv run pytest` | Run tests |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `uv run pyright` | Type check |

## Stripe local dev

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
# Copy the printed whsec_... into .env as STRIPE_WEBHOOK_SECRET
```

## Health endpoints

- `GET /healthz` → `ok` (liveness)
- `GET /readyz` → `ready` (readiness — checks DB)

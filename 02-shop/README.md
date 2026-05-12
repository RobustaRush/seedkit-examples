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

# 02-shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- **Django** (split settings: base / local / production)
- **PostgreSQL** via psycopg
- **django-allauth** — email login, mandatory email verification in production
- **django-axes** — brute-force lockout
- **WhiteNoise** — static file serving in production
- **Tailwind CSS** (standalone CLI) + **DaisyUI** — no Node.js
- **Stripe** raw SDK — checkout, customer portal, webhook
- **Ruff** — lint + format
- **pytest** + pytest-django — test runner
- **pyright** + django-stubs — type checking
- **mise** — task runner

## Setup

```sh
cp .env.example .env
# Edit .env: set a real DJANGO_SECRET_KEY and database credentials
createdb shop_db
mise run install
mise run migrate
mise run superuser
```

## Commands

| Task | Command |
|------|---------|
| Dev server | `mise run dev` |
| Migrate | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Shell | `mise run shell` |
| Create superuser | `mise run superuser` |
| Tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Collect static | `mise run collectstatic` |

Without mise: `uv run manage.py <command>` or `uv run pytest` / `uv run ruff check .`.

## Environment variables

See `.env.example` for the full list. Key variables:

- `DJANGO_SECRET_KEY` — required in production
- `DJANGO_DEBUG` — `True` in dev, unset in production
- `DJANGO_ALLOWED_HOSTS` — comma-separated list
- `DATABASE_URL` — postgres connection string
- `EMAIL_URL` — `consolemail://` in dev, `smtp+tls://user:pass@host:587` in production
- `DEFAULT_FROM_EMAIL` — sender address
- `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET`

## Stripe

Local webhook forwarding:

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
```

Use the printed `whsec_...` as `STRIPE_WEBHOOK_SECRET` in `.env`.

## Health checks

- `GET /healthz` — liveness (process alive)
- `GET /readyz` — readiness (DB reachable)

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

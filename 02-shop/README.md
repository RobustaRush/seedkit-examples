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

Small e-commerce site with Django admin and SMTP transactional email.

## Stack

| Layer | Package |
|---|---|
| Framework | Django 6.x |
| Database | PostgreSQL (`psycopg[binary]`) |
| Auth | `django-allauth` — email login, mandatory email verification |
| Auth hardening | `django-axes` — brute-force lockout |
| Static files | WhiteNoise |
| Frontend | `django-tailwind-cli` + DaisyUI |
| Billing | `stripe` raw SDK |
| Settings | `django-environ`, split `base/local/production` |
| Linting | Ruff |
| Tests | pytest + pytest-django |
| Types | pyright + django-stubs |
| Tasks | mise |

## Local setup

```sh
# 1. Create the database
createdb shop_db

# 2. Install dependencies
mise run install   # or: uv sync

# 3. Copy env and set a real secret key
cp .env.example .env
# edit .env — DATABASE_URL is already set for local postgres

# 4. Migrate
mise run migrate

# 5. Create a superuser (interactive)
mise run superuser

# 6. Build CSS
mise run tailwind

# 7. Start dev server (with Tailwind watcher)
mise run dev
```

Open <http://127.0.0.1:8000/> to see the index page.  
Open <http://127.0.0.1:8000/admin/> to access the admin.

## Common tasks

| Task | Command |
|---|---|
| Dev server + watcher | `mise run dev` |
| Run migrations | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Django shell | `mise run shell` |
| Collect static | `mise run collectstatic` |

Without mise: `uv run manage.py <command>` / `uv run pytest` / `uv run ruff check .`

## Key endpoints

| Path | Description |
|---|---|
| `/` | Index page |
| `/admin/` | Django admin |
| `/accounts/login/` | Allauth login |
| `/accounts/signup/` | Allauth signup |
| `/billing/checkout/` | Stripe Checkout (POST, login required) |
| `/billing/portal/` | Stripe Customer Portal (login required) |
| `/billing/webhook/` | Stripe webhook receiver |
| `/healthz` | Liveness probe |
| `/readyz` | Readiness probe (checks DB) |
| `/robots.txt` | Robots file |

## Stripe

For local webhook testing:

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
# paste the printed whsec_... into .env as STRIPE_WEBHOOK_SECRET
```

## Environment variables

See `.env.example` for the full list. Key vars:

- `DJANGO_SECRET_KEY` — required in production
- `DJANGO_DEBUG` — `True` in dev, unset in production
- `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames
- `DATABASE_URL` — postgres connection string
- `EMAIL_URL` — `consolemail://` (dev) or `smtp+tls://...` (prod)
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

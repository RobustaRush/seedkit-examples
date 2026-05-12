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

| Component | Package |
|---|---|
| Framework | Django 6 |
| Database | PostgreSQL (`psycopg[binary]`) |
| Auth | `django-allauth` (email login, mandatory email verification) |
| Auth hardening | `django-axes` brute-force lockout |
| Static files | WhiteNoise |
| Frontend | Tailwind CSS 4 via `django-tailwind-cli` + DaisyUI |
| Billing | Stripe SDK |
| Email | SMTP (console in dev, SMTP in production) |
| Task runner | mise |
| Linting | Ruff |
| Tests | pytest + pytest-django |
| Type checking | pyright + django-stubs |
| Production server | gunicorn |
| Deploy | VPS, Docker + Caddy |

## Quick start

```sh
cp .env.example .env
# Edit .env: set DJANGO_SECRET_KEY and DATABASE_URL
createdb shop_db
mise run migrate
mise run dev
```

## Commands

| Task | Command |
|---|---|
| Install deps | `mise run install` |
| Dev server (Tailwind watch included) | `mise run dev` |
| Migrate | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Shell | `mise run shell` |
| Create superuser | `mise run superuser` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Collect static | `mise run collectstatic` |
| Build Tailwind CSS | `mise run tailwind` |

Fallback (no mise): `uv run manage.py <cmd>`.

## Environment variables

Copy `.env.example` to `.env` and fill in:

- `DJANGO_SECRET_KEY` — 50+ random chars
- `DATABASE_URL` — `postgres://postgres:postgres@localhost:5432/shop_db`
- `EMAIL_URL` — `consolemail://` for dev, `smtp+tls://user:pass@host:587` for prod
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

## Production

### Build and push image

```sh
docker build -t ghcr.io/yourgithubuser/02-shop:latest -f Dockerfile .
docker push ghcr.io/yourgithubuser/02-shop:latest
```

### Deploy to VPS

```sh
ssh user@vps
cd /srv/02-shop
git pull
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate --noinput
docker compose -f deploy/docker-compose.prod.yml up -d
```

Update `deploy/docker-compose.prod.yml` image name and `deploy/Caddyfile` domain before first deploy.

### Required prod env vars (`.env.prod` on VPS)

```
DJANGO_SECRET_KEY=<50+ char random key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
DJANGO_BEHIND_PROXY=True
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgres://postgres:<POSTGRES_PASSWORD>@db:5432/shop_db
POSTGRES_PASSWORD=<secure password>
EMAIL_URL=smtp+tls://user:pass@smtp.provider.com:587
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Stripe webhook (local dev)

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
# Use the printed whsec_... as STRIPE_WEBHOOK_SECRET in .env
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

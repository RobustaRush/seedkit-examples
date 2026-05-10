## Issues

No issues found after fix below.

## Fixes applied

**`config/asgi.py:14`** — pointed at empty settings package `"config.settings"` instead of `"config.settings.production"`. Would raise `ImproperlyConfigured` immediately on ASGI startup (`SECRET_KEY`, `INSTALLED_APPS`, etc. are only in the split-settings modules, not `__init__.py`). Fixed to `"config.settings.production"` to match `config/wsgi.py`.

## What worked out of the box

- Split settings (`base`, `local`, `production`) loaded correctly
- Custom `users.User` (email-only) with `stripe_customer_id`, migrations present
- `django-allauth` + `django-axes` wired: `AxesBackend` first, `AxesMiddleware` last, `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`
- WhiteNoise middleware in `production.py` only; `CompressedManifestStaticFilesStorage` configured
- Email: `consolemail://` default in base (gated by `DEBUG`), SMTP in production via `EMAIL_URL`
- `django-tailwind-cli` + DaisyUI: `source.css` with `@plugin "./daisyui.mjs"`, both `.mjs` bundles committed, `TAILWIND_CLI_VERSION = "4.1.3"` pinned
- `base.html` has `{% load tailwind_cli %}`, `{% tailwind_css %}`, `data-theme="light"`
- `index.html` contains `text-blue-600`, `text-4xl`, `btn btn-primary`
- Health checks `/healthz` → `ok`, `/readyz` → `ready`
- `robots.txt` returns `User-agent: *` / `Disallow: /admin/` (when `DEBUG=False`)
- Stripe: `stripe` in runtime deps, env vars in `.env.example`, `billing/` app with `@csrf_exempt` + `construct_event` webhook, `stripe_customer_id` on `User`
- `ruff check .` exits 0; `pyright` exits 0 (0 errors, 0 warnings)

## What broke

- `config/asgi.py` referenced `config.settings` (empty `__init__.py`) — see Fixes applied.

## Suggested skill changes

- After generating split settings, auto-update `config/asgi.py` in the same step as `config/wsgi.py` and `manage.py`.

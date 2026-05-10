No issues found.

The boot path checks out: `manage.py:9` defaults to `config.settings.local`, `config/wsgi.py:14` and `config/celery.py:5` to `config.settings.production`. Required-secret gating in `config/settings/base.py:11-13` (`env.NOTSET` when `DEBUG` is False) is consistent with the secrets enumerated in `fly.toml:13-23`. The `/readyz` endpoint in `pages/views.py:10` performs `SELECT 1` and is exempted from HTTPS redirect via `config/settings/production.py:8` `SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]` (Django strips the leading slash before matching, so this matches). Production middleware/CSP, axes, mailauth ordering, S3 storage selection, and proxy header handling all look coherent. Smoke tests in `pages/tests.py` exercise both endpoints. No exposed secrets, no auth bypass on the WSGI app, and the unauthenticated `/users/{user_id}` in `api/api.py:14` runs only on the `bolt` process which `fly.toml` does not expose via a `[[services]]` block.

## Fixes applied

- `templates/base.html:7` reads `{{ ANALYTICS_ID }}` but no context processor injected it. Added `pages/context_processors.analytics` and registered it in `config/settings/base.py` `TEMPLATES[0]["OPTIONS"]["context_processors"]`.

## Suggested skill changes

- `references/rest-bolt.md` implies `config/urls_bolt.py` should wire `api.urls`, but `BoltAPI()` has no `.urls` attribute — `runbolt` auto-discovers APIs. The reference should clarify that the bolt URLConf is a minimal valid Django URLconf (`urlpatterns: list = []`) and that route discovery is handled by the `runbolt` management command, not the URLconf.
- The smoke test runs `curl` from inside the slim runtime container, but the `python:3.12-slim-bookworm` image has no `curl`. Test should curl from the host against the exposed port, or install curl in the dev stage only.

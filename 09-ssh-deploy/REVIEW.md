No issues found.

Notes for context:
- `config/settings/production.py:5` exempts `^healthz$`/`^readyz$` from SSL redirect, matching the URL paths in `config/urls.py:10`.
- `Dockerfile:29` runs `collectstatic` with `DJANGO_DEBUG=True` so `SECRET_KEY` defaults instead of failing the build.
- `deploy/docker-compose.prod.yml:7` binds `127.0.0.1:8000:8000` (no public port), and `.github/workflows/deploy.yml:45` passes `--env-file deploy/.env.prod` so `${GITHUB_REPOSITORY}` and `${POSTGRES_PASSWORD}` interpolate.
- Static files are not served by gunicorn (no WhiteNoise in MIDDLEWARE), but admin assets working assumes a host-level reverse proxy — design choice for this scaffold, not a boot blocker.

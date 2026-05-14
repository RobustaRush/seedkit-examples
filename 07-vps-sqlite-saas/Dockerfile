# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# collectstatic runs in the builder so the prod image ships compressed assets.
# DJANGO_DEBUG=True unlocks dev defaults (no real SECRET_KEY/DATABASE_URL needed).
RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    /opt/venv/bin/python manage.py collectstatic --noinput


FROM python:3.12-slim-bookworm AS prod

ENV PATH="/opt/venv/bin:$PATH"

# Install Litestream from the official .deb release.
# dpkg --print-architecture resolves amd64/arm64 so the image builds on M-series Macs.
RUN apt-get update \
 && apt-get install -y --no-install-recommends wget \
 && ARCH=$(dpkg --print-architecture) \
 && wget -q "https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-linux-${ARCH}.deb" \
 && dpkg -i "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

# Pre-create /data before `USER django` — named volume mounts as root:root,
# so the django user can't create site.sqlite3 / WAL files otherwise.
RUN mkdir -p /data && chown django:django /data

# Pre-create /app/media for the same reason (media volume).
RUN mkdir -p /app/media && chown django:django /app/media

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

# Bake Litestream config and entrypoint into the image at fixed paths.
COPY litestream.yml /etc/litestream.yml
COPY --chmod=755 entrypoint.sh /entrypoint.sh

USER django

ENTRYPOINT ["/entrypoint.sh"]
CMD []

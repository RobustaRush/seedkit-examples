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

RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    /opt/venv/bin/python manage.py collectstatic --noinput


FROM python:3.12-slim-bookworm AS prod
ENV PATH="/opt/venv/bin:$PATH"

# Install Litestream for SQLite replication — arch-aware so the image builds on M-series Macs too
RUN apt-get update && apt-get install -y --no-install-recommends wget \
 && ARCH=$(dpkg --print-architecture) \
 && wget -q "https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-linux-${ARCH}.deb" \
 && dpkg -i "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

# Pre-create data and media dirs before USER django so the volume mounts are writable
RUN mkdir -p /data /app/media && chown django:django /data /app/media

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER django

ENTRYPOINT ["/entrypoint.sh"]
CMD []

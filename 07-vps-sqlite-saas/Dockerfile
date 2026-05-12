# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install Litestream — arch-aware so the image builds on M-series Macs too
RUN apt-get update && apt-get install -y --no-install-recommends wget \
 && ARCH=$(dpkg --print-architecture) \
 && wget -q "https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-linux-${ARCH}.deb" \
 && dpkg -i "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app

COPY --chown=django:django pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY --chown=django:django . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Pre-create persistent-volume mount points with correct ownership before switching user.
# Named volumes mount as root:root on first creation; the django user can't write otherwise.
RUN mkdir -p /data && chown django:django /data
RUN mkdir -p /app/media && chown django:django /app/media

# Collect static files (DJANGO_DEBUG=True lets dev defaults fill in SECRET_KEY/DATABASE_URL)
RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    python manage.py collectstatic --noinput

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY litestream.yml /etc/litestream.yml

USER django

ENTRYPOINT ["/entrypoint.sh"]

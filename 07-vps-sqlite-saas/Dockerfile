FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Install Litestream (architecture-aware — works on amd64 and arm64)
RUN apt-get update && apt-get install -y --no-install-recommends wget \
 && ARCH=$(dpkg --print-architecture) \
 && wget -q "https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-linux-${ARCH}.deb" \
 && dpkg -i "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm "litestream-v0.3.13-linux-${ARCH}.deb" \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app

COPY --chown=django:django pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=django:django . .
RUN uv sync --frozen --no-dev

# Pre-create media dir with correct ownership before USER switch
RUN mkdir -p /app/media && chown django:django /app/media

# collectstatic: DJANGO_DEBUG=True unlocks dev defaults so manage.py boots
# without real SECRET_KEY/DATABASE_URL; production.py applies manifest storage.
RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    python manage.py collectstatic --noinput

COPY --chown=django:django litestream.yml /etc/litestream.yml
COPY --chown=root:root entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER django

ENTRYPOINT ["/entrypoint.sh"]

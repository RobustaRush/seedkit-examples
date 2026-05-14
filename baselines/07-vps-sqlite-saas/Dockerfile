# ---- build stage --------------------------------------------------------
FROM python:3.12-slim AS build

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
# Install runtime deps only (no [dev] extras)
RUN uv pip install --system --no-deps --no-cache ".[dev]" 2>/dev/null; \
    uv pip install --system --no-cache .

COPY . .

# Collect static files with a throwaway secret key
RUN SECRET_KEY=build-placeholder \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput


# ---- production stage ---------------------------------------------------
FROM python:3.12-slim AS production

WORKDIR /app

# Litestream
ARG LITESTREAM_VERSION=0.3.13
RUN ARCH="$(dpkg --print-architecture)" && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -fsSL \
      "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-${ARCH}.deb" \
      -o /tmp/litestream.deb && \
    dpkg -i /tmp/litestream.deb && \
    rm /tmp/litestream.deb && \
    apt-get purge -y curl && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages and static artefacts from build stage
COPY --from=build /usr/local/lib/python3.12/site-packages \
                  /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Data dir — host volume is mounted here by docker-compose
RUN mkdir -p /data

ENV DJANGO_SETTINGS_MODULE=config.settings.production
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

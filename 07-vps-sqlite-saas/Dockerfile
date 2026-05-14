# ---------- build stage ----------
FROM python:3.12-slim AS build

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

# ---------- prod stage ----------
FROM python:3.12-slim AS prod

WORKDIR /app

# Install Litestream from the official .deb (arch-aware)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && \
    LITESTREAM_VERSION=0.3.13 && \
    ARCH=$(dpkg --print-architecture) && \
    curl -fsSL "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-${ARCH}.deb" \
        -o /tmp/litestream.deb && \
    dpkg -i /tmp/litestream.deb && \
    rm /tmp/litestream.deb && \
    apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Copy venv + app from build stage
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Create non-root user
RUN addgroup --system django && adduser --system --ingroup django django

# Data directory (mounted from host)
RUN mkdir -p /data && chown django:django /data

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER django

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

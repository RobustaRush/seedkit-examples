# ── prod ──────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS prod

WORKDIR /app

# Install system deps + Litestream
ARG LITESTREAM_VERSION=0.3.13
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && ARCH=$(dpkg --print-architecture) \
    && curl -fsSL "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-${ARCH}.deb" \
       -o /tmp/litestream.deb \
    && dpkg -i /tmp/litestream.deb \
    && rm /tmp/litestream.deb \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django && adduser --system --ingroup django django

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies into /app/.venv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY . .

RUN mkdir -p /data /app/staticfiles /app/media \
    && chown -R django:django /data /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE="config.settings.production"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER django

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

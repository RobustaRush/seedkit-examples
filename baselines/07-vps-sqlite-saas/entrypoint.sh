#!/bin/sh
set -e

DB_PATH="/data/db.sqlite3"
CACHE_DB_PATH="/data/cache.sqlite3"

# Restore main DB from replica if this is a fresh volume
if [ ! -f "$DB_PATH" ]; then
    echo "No local database found — attempting restore from replica..."
    litestream restore -if-replica-exists -o "$DB_PATH" "${LITESTREAM_REPLICA_URL}" || \
        echo "No replica found or restore skipped; starting fresh."
fi

# Apply Django migrations
python manage.py migrate --noinput

# Create cache table if the cache DB is fresh
python manage.py createcachetable --database=cache 2>/dev/null || true

# Run django-tasks migrations (they target the default DB)
# Already covered by manage.py migrate above.

# Hand off to Litestream which execs gunicorn as its child process
exec litestream replicate \
    -config /app/litestream.yml \
    -exec "gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-2} \
        --threads ${GUNICORN_THREADS:-4} \
        --timeout ${GUNICORN_TIMEOUT:-30} \
        --access-logfile -"

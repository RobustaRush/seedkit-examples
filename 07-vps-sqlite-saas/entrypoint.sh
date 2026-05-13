#!/bin/sh
set -e

# Pass-through for smoke tests / one-off commands
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

DB_PATH="${DB_PATH:-/data/db.sqlite3}"

# Restore database from S3 if it doesn't already exist
if [ ! -f "$DB_PATH" ]; then
    echo "Restoring database from Litestream..."
    litestream restore -if-replica-exists -o "$DB_PATH" \
        "s3://${LITESTREAM_S3_BUCKET}/db.sqlite3" || true
fi

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Litestream replication and gunicorn
exec litestream replicate -exec \
    "gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"

#!/bin/sh
set -e

DB_PATH="${DATABASE_URL#sqlite:////}"
DB_PATH="/${DB_PATH}"  # restore leading slash stripped by parameter expansion

# Restore from Litestream replica if DB doesn't exist yet
if [ ! -f "$DB_PATH" ]; then
    echo "Restoring database from replica..."
    litestream restore -if-replica-exists -o "$DB_PATH" "s3://${LITESTREAM_BUCKET}/db"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec litestream replicate \
    -config /app/litestream.yml \
    -exec "gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"

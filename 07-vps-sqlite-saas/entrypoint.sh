#!/bin/sh
set -eu

# Pass-through for ad-hoc commands (e.g. `docker run img which gunicorn`, `id -un`).
# Without this, the entrypoint hijacks every invocation and smoke checks fail.
if [ "$#" -gt 0 ]; then exec "$@"; fi

mkdir -p /data

# Restore from S3 replica if the DB doesn't exist yet and a replica is available.
litestream restore -config /etc/litestream.yml -if-db-not-exists -if-replica-exists /data/site.sqlite3

python manage.py migrate --noinput
python manage.py createcachetable --database cache

# Run gunicorn under litestream so every WAL frame is streamed to S3.
exec litestream replicate -config /etc/litestream.yml \
    -exec "gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 2 --timeout 30"

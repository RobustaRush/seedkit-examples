#!/bin/sh
set -eu

# Pass-through for ad-hoc commands (`docker run img which gunicorn`, `id -un`).
# Without this, the entrypoint hijacks every invocation and the smoke checks fail.
if [ "$#" -gt 0 ]; then exec "$@"; fi

mkdir -p /data
litestream restore -config /etc/litestream.yml -if-db-not-exists -if-replica-exists /data/site.sqlite3
litestream restore -config /etc/litestream.yml -if-db-not-exists -if-replica-exists /data/cache.sqlite3
python manage.py migrate --noinput
python manage.py createcachetable --database cache
exec litestream replicate -config /etc/litestream.yml \
    -exec "gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 2 --timeout 30"

#!/bin/sh
set -eu

# Pass-through: when called with args (e.g. `docker run img which gunicorn`)
# exec them directly so smoke-test commands work against the image.
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

mkdir -p /data
litestream restore -config /etc/litestream.yml -if-db-not-exists -if-replica-exists /data/site.sqlite3
python manage.py migrate --noinput
python manage.py createcachetable --database cache
exec litestream replicate -config /etc/litestream.yml -exec "gunicorn config.wsgi --bind 0.0.0.0:8000"

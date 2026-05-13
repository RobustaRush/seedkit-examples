# 06-silk-lab

Profile request paths with django-silk and run background tasks on the DB backend.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 5.1+ |
| Database | PostgreSQL (host) |
| Profiling | django-silk |
| Background tasks | django-tasks (DB backend) |
| Analytics | GoatCounter (self-hosted) |
| Email | Console (local) |
| DX | ruff, pytest, django-extensions |
| DB safety | django-zeal, django-migration-linter, django-test-migrations |

## Quick start

```sh
createdb silk_db
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
# In a second terminal:
uv run manage.py db_worker
```

## Enqueue a task

```python
# uv run manage.py shell
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue("you@example.com")
```

## Silk profiling

Visit http://localhost:8000/silk/ to inspect requests and queries.

Decorate a function with `@silk_profile()`:

```python
from silk.profiling.profiler import silk_profile

@silk_profile(name="my_view")
def my_view(request):
    ...
```

## GoatCounter

Set `GOATCOUNTER_URL` to your self-hosted counter endpoint:

```sh
export GOATCOUNTER_URL=https://stats.example.com/count
```

The snippet is included in `templates/base.html` when the variable is set.

## Commands

```sh
uv run manage.py lintmigrations     # check migrations for safety
uv run ruff check .                 # lint
uv run pytest                       # run tests
uv run manage.py show_urls          # list all URL patterns
```

Built with [Seedkit](https://github.com/RobustaRush/seedkit).

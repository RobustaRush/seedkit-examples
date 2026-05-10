# 01-minimal-blog

A tiny blog scaffold to verify the seedkit skill works end-to-end.

## Stack

- Python 3.12+, Django 6, SQLite
- django-environ for settings
- Console email backend

## Setup

```sh
cp .env.example .env          # edit DJANGO_SECRET_KEY with a real value
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open http://127.0.0.1:8000/admin/

## Commands

| Command | Description |
|---|---|
| `uv run manage.py runserver` | Start dev server |
| `uv run manage.py migrate` | Apply migrations |
| `uv run manage.py test` | Run tests |
| `uv run manage.py createsuperuser` | Create admin user |

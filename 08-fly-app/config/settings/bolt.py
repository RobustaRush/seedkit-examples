from .base import *  # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE

_DROP_MIDDLEWARE = {
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
}
MIDDLEWARE = [m for m in MIDDLEWARE if m not in _DROP_MIDDLEWARE]

_DROP_APPS = {
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
}
INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in _DROP_APPS]

TEMPLATES = []

ROOT_URLCONF = "config.urls_bolt"

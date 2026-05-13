from .base import *  # noqa: F401, F403

ROOT_URLCONF = "config.urls_bolt"
TEMPLATES = []

INSTALLED_APPS = [
    app
    for app in INSTALLED_APPS  # noqa: F405
    if app
    not in {
        "django.contrib.admin",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    }
]

MIDDLEWARE = [
    m
    for m in MIDDLEWARE  # noqa: F405
    if m
    not in {
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
    }
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

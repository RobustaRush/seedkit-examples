from .base import *  # noqa: F401, F403

_strip_apps = {
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
}
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in _strip_apps]  # noqa: F405

_strip_middleware = {
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
}
MIDDLEWARE = [m for m in MIDDLEWARE if m not in _strip_middleware]  # noqa: F405

TEMPLATES: list = []
ROOT_URLCONF = "config.urls_bolt"

from .base import *  # noqa: F401, F403

SECRET_KEY = "django-insecure-local-dev-secret-key-change-in-production"

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]

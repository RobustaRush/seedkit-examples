import environ

from .base import *  # noqa: F401, F403

env = environ.Env()

vars().update(env.email_url("EMAIL_URL", default="consolemail://"))  # type: ignore[arg-type]
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")  # type: ignore[arg-type]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
X_FRAME_OPTIONS = "DENY"

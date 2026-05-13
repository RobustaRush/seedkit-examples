import sentry_sdk
from environs import Env
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .base import *  # noqa: F401, F403

env = Env()
env.read_env()

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Email via SMTP (Postmark)
EMAIL_URL = env.str("EMAIL_URL")
_email = env.dj_email_url("EMAIL_URL")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = _email["EMAIL_HOST"]
EMAIL_PORT = _email["EMAIL_PORT"]
EMAIL_HOST_USER = _email["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = _email["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = _email.get("EMAIL_USE_TLS", True)

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="noreply@example.com")
SERVER_EMAIL = env.str("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
ADMINS = [("Admin", e) for e in env.list("DJANGO_ADMINS", default=[])]

# Security hardening
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Sentry
sentry_sdk.init(
    dsn=env.str("SENTRY_DSN", default=""),
    integrations=[
        DjangoIntegration(),
        LoggingIntegration(level=None, event_level=None),
    ],
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
    send_default_pii=False,
)

# Structured logging — JSON
import logging  # noqa: E402
import structlog  # noqa: E402

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

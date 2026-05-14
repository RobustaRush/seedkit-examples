import logging

import sentry_sdk
import structlog
from environs import Env
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.rq import RqIntegration

from .base import *  # noqa: F401, F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# HTTPS / Security hardening
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# CSP — allow Umami script from configured host
_umami_host = env("UMAMI_HOST", default="")
_script_srcs = ["'self'", _umami_host] if _umami_host else ["'self'"]
_connect_srcs = ["'self'", _umami_host] if _umami_host else ["'self'"]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": _script_srcs,
        "style-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'"],
        "connect-src": _connect_srcs,
        "frame-ancestors": ["'none'"],
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django_structlog": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


def _scrub_pii(event: dict, hint: dict) -> dict | None:
    """Remove PII from error reports before sending to Bugsink/Sentry."""
    if "user" in event:
        event["user"].pop("ip_address", None)
        event["user"].pop("email", None)
    if "request" in event:
        headers = event["request"].get("headers", {})
        for key in list(headers.keys()):
            if key.lower() in ("cookie", "authorization", "x-api-key", "x-forwarded-for"):
                headers[key] = "[Scrubbed]"
    return event


sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=""),
    integrations=[
        DjangoIntegration(),
        RqIntegration(),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    traces_sample_rate=0.1,
    send_default_pii=False,  # GDPR: never send PII automatically
    before_send=_scrub_pii,
)

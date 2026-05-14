import structlog

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.rq import RqIntegration

from .base import *  # noqa: F401, F403
from .base import UMAMI_URL, env

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 63072000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

# JSON structlog for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structlog_json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structlog_json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}


def _scrub_pii(event, hint):
    for scope in ("request", "user"):
        if scope in event:
            event[scope].pop("email", None)
            event[scope].pop("username", None)
            event[scope].pop("ip_address", None)
    if "request" in event:
        event["request"].pop("cookies", None)
        headers = event["request"].get("headers", {})
        headers.pop("Authorization", None)
        headers.pop("Cookie", None)
    return event


# Bugsink / Sentry error reporting
_sentry_dsn = env("SENTRY_DSN", default="")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[DjangoIntegration(), RqIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        before_send=_scrub_pii,
    )

# Loosen CSP for self-hosted Umami
if UMAMI_URL:
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["script-src"] = ("'self'", UMAMI_URL)  # type: ignore[index]
    CONTENT_SECURITY_POLICY["DIRECTIVES"]["connect-src"] = ("'self'", UMAMI_URL)  # type: ignore[index]

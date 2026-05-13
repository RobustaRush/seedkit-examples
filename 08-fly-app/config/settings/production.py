import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"

def _before_send(event: dict, hint: dict) -> dict | None:  # noqa: ANN001
    """Scrub PII from error reports."""
    if "user" in event:
        event["user"] = {"id": event["user"].get("id")}
    request = event.get("request", {})
    if "headers" in request:
        request["headers"].pop("Cookie", None)
        request["headers"].pop("Authorization", None)
    if "env" in request:
        request["env"] = {}
    return event


sentry_sdk.init(
    dsn=GLITCHTIP_DSN,  # noqa: F405
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    before_send=_before_send,
)

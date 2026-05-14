from .base import *  # noqa: F401, F403

import environ
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()

DATABASES = {"default": env.db("DATABASE_URL")}

EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
POSTMARK_SERVER_TOKEN = env("POSTMARK_SERVER_TOKEN")
ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": POSTMARK_SERVER_TOKEN,
    "WEBHOOK_SECRET": env("ANYMAIL_WEBHOOK_SECRET", default=""),
}

AXES_HANDLER = "axes.handlers.cache.AxesCacheHandler"

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


def _scrub_pii(event: dict, hint: object) -> dict:
    if "request" in event:
        event["request"].pop("cookies", None)
        event["request"].pop("headers", None)
        data = event["request"].get("data", {})
        for key in ("password", "token", "email", "username"):
            if isinstance(data, dict):
                data.pop(key, None)
    if "user" in event:
        event["user"] = {"id": event["user"].get("id")}
    return event


GLITCHTIP_DSN = env("GLITCHTIP_DSN", default="")
if GLITCHTIP_DSN:
    sentry_sdk.init(
        dsn=GLITCHTIP_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        before_send=_scrub_pii,
    )

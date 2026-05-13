import sentry_sdk

from .base import *  # noqa: F401, F403
from .base import UMAMI_HOST, env

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks — GDPR retention default
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── CSP — tightened for production (django-csp 4.x format) ───────────────────
_umami_origin = (UMAMI_HOST,) if UMAMI_HOST else ()
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",) + _umami_origin,
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'",) + _umami_origin,
    }
}

# ── Error reporting — Bugsink (sentry-sdk DSN) ───────────────────────────────
def _strip_pii(event, hint):
    """Remove PII from error reports before sending to Bugsink."""
    if "request" in event:
        event["request"].pop("cookies", None)
        hdrs = event["request"].get("headers", {})
        for key in ("Authorization", "Cookie", "X-Csrftoken"):
            hdrs.pop(key, None)
    if "user" in event:
        event["user"] = {"id": event["user"].get("id")}
    return event


sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=""),
    send_default_pii=False,
    before_send=_strip_pii,
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
    environment=env("SENTRY_ENVIRONMENT", default="production"),
)

# ── GDPR data retention ───────────────────────────────────────────────────────
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # keep sessions within SESSION_COOKIE_AGE

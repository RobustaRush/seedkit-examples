from .base import *
from .base import (
    AWS_S3_CUSTOM_DOMAIN,
    AWS_S3_ENDPOINT_URL,
    AWS_S3_REGION_NAME,
    AWS_S3_URL_PROTOCOL,
    AWS_STORAGE_BUCKET_NAME,
    MIDDLEWARE,
    STORAGES,
    env,
)

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Static files on S3
STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        "OPTIONS": {"location": "static"},
    },
}

if AWS_S3_CUSTOM_DOMAIN:
    STATIC_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/static/"
elif AWS_S3_ENDPOINT_URL:
    STATIC_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/static/"
else:
    _region = "" if AWS_S3_REGION_NAME == "us-east-1" else f".{AWS_S3_REGION_NAME}"
    STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3{_region}.amazonaws.com/static/"

# CSP
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", "https://www.googletagmanager.com"),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:", "https://www.google-analytics.com"),
        "font-src": ("'self'",),
        "connect-src": (
            "'self'",
            "https://www.google-analytics.com",
            "https://www.googletagmanager.com",
        ),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}

# GlitchTip / Sentry error reporting
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    def _scrub(event, hint):
        request = event.get("request") or {}
        headers = request.get("headers") or {}
        for h in ("Authorization", "Cookie"):
            headers.pop(h, None)
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        release=env("SENTRY_RELEASE", default=None),
        send_default_pii=False,
        before_send=_scrub,
    )

from .base import *
from .base import (
    AWS_S3_CUSTOM_DOMAIN,
    AWS_S3_ENDPOINT_URL,
    AWS_S3_REGION_NAME,
    AWS_S3_URL_PROTOCOL,
    AWS_STORAGE_BUCKET_NAME,
    STORAGES,
    env,
)

# Needed for the MIDDLEWARE reassignment below; importing it avoids an
# undefined-name error from pyright while ruff ignores the F811.
from .base import MIDDLEWARE as _MIDDLEWARE_BASE  # noqa: F401

# ── HTTPS / proxy ────────────────────────────────────────────────────────────
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

# ── CSP ──────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": (
            "'self'",
            "https://www.googletagmanager.com",
            "https://www.google-analytics.com",
        ),
        "style-src": ("'self'", "'unsafe-inline'"),  # admin requires unsafe-inline
        "img-src": ("'self'", "data:", "https://www.google-analytics.com"),
        "font-src": ("'self'",),
        "connect-src": (
            "'self'",
            "https://www.googletagmanager.com",
            "https://www.google-analytics.com",
        ),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}

# ── S3 static in production ───────────────────────────────────────────────────
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

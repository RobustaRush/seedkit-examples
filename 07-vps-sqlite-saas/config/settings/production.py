import environ

from .base import *

env = environ.Env()

# SQLite WAL + tuning
DATABASES["default"]["OPTIONS"] = {
    "transaction_mode": "IMMEDIATE",
    "timeout": 5,
    "init_command": (
        "PRAGMA journal_mode=WAL;"
        "PRAGMA synchronous=NORMAL;"
        "PRAGMA mmap_size=134217728;"
        "PRAGMA journal_size_limit=27103364;"
        "PRAGMA cache_size=2000;"
    ),
}
DATABASES["cache"]["OPTIONS"] = DATABASES["default"]["OPTIONS"]

# HTTPS
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Allauth: mandatory email verification in prod
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# 2FA: force reauthentication in prod
ACCOUNT_REAUTHENTICATION_REQUIRED = True

# WhiteNoise
sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
MIDDLEWARE.insert(sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# CSP
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'",),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}

# Sentry
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        release=env("SENTRY_RELEASE", default=None),
    )

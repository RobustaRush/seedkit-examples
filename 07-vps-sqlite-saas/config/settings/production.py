from .base import *  # noqa: F401, F403

_SQLITE_OPTIONS = {
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

# SQLite production tuning
DATABASES["default"]["OPTIONS"] = _SQLITE_OPTIONS  # noqa: F405
DATABASES["cache"]["OPTIONS"] = _SQLITE_OPTIONS  # noqa: F405

# allauth: mandatory email verification in prod
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# allauth MFA
ACCOUNT_REAUTHENTICATION_REQUIRED = True

# WhiteNoise
sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")  # noqa: F405
MIDDLEWARE.insert(sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# HTTPS / security
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

if env.bool("DJANGO_BEHIND_PROXY", default=False):  # noqa: F405
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])  # noqa: F405

# CSP
MIDDLEWARE = [*MIDDLEWARE, "csp.middleware.CSPMiddleware"]  # noqa: F405

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
SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        release=env("SENTRY_RELEASE", default=None),  # noqa: F405
    )

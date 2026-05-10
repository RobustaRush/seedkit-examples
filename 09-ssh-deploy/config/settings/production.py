from .base import *  # noqa: F401, F403

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]

if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# CSP — production only; runserver skips this middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.logging.RequestContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Build script-src dynamically so the Umami host resolves from env at runtime.
# ANALYTICS_HOST is already bound via base.py's env() call (imported above).
_script_src = ["'self'"]
if ANALYTICS_HOST:
    _script_src.append(ANALYTICS_HOST)

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": tuple(_script_src),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:"),
        "font-src": ("'self'",),
        "connect-src": ("'self'",) + ((ANALYTICS_HOST,) if ANALYTICS_HOST else ()),
        "frame-ancestors": ("'none'",),
        "base-uri": ("'self'",),
        "form-action": ("'self'",),
    },
}

# Bugsink error reporting
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
        send_default_pii=False,
        before_send=_scrub,
        release=env("SENTRY_RELEASE", default=None),
    )

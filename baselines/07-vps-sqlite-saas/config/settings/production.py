from pathlib import Path

import sentry_sdk

from .base import *  # noqa: F401, F403
from .base import DATABASES, env

# Hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Security
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Production DB lives in the Docker volume at /data/
DATABASES["default"]["NAME"] = Path("/data/db.sqlite3")
DATABASES["cache"]["NAME"] = Path("/data/cache.sqlite3")

# Email via SMTP (Postmark or any SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
_email_url = env.str("EMAIL_URL", default="")
if _email_url:
    _email = env.dj_email_url("EMAIL_URL")
    EMAIL_HOST = _email["EMAIL_HOST"]
    EMAIL_PORT = _email["EMAIL_PORT"]
    EMAIL_HOST_USER = _email["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = _email["EMAIL_HOST_PASSWORD"]
    EMAIL_USE_TLS = _email.get("EMAIL_USE_TLS", False)
    EMAIL_USE_SSL = _email.get("EMAIL_USE_SSL", False)

# Tighter CSP for production
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_UPGRADE_INSECURE_REQUESTS = True

# Sentry
_sentry_dsn = env.str("SENTRY_DSN", default="")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
        send_default_pii=False,
    )

from .base import *

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

# Allauth — mandatory email verification in production
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# 2FA settings
MFA_TOTP_ISSUER = env("DJANGO_SITE_DOMAIN", default="example.com")
ACCOUNT_REAUTHENTICATION_REQUIRED = True

# WhiteNoise manifest storage
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# CSP
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.logging.RequestContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "axes.middleware.AxesMiddleware",
]

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

# dbbackup
if not DEBUG:
    INSTALLED_APPS += ["dbbackup"]

    DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DBBACKUP_STORAGE_OPTIONS = {
        "access_key": env("AWS_ACCESS_KEY_ID"),
        "secret_key": env("AWS_SECRET_ACCESS_KEY"),
        "bucket_name": env("DBBACKUP_BUCKET"),
        "default_acl": "private",
    }

    DBBACKUP_CLEANUP_KEEP = 14
    DBBACKUP_CLEANUP_KEEP_MEDIA = 7
    DBBACKUP_FILENAME_TEMPLATE = "{databasename}-{servername}-{datetime}.{extension}"

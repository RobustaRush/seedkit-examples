from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-build-only" if DEBUG else env.NOTSET)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"] if DEBUG else env.NOTSET)
DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///{}".format(BASE_DIR / "db.sqlite3") if DEBUG else env.NOTSET)}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    # mailauth.contrib.admin MUST come before django.contrib.admin
    "mailauth.contrib.admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mailauth",
    "axes",
    "anymail",
    "django_bolt",
    "pages",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # MUST be last — wraps every other middleware's auth attempts
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    # AxesBackend MUST be first
    "axes.backends.AxesBackend",
    "mailauth.backends.MailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pages.context_processors.analytics",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --------------------------------------------------------------------------
# Redis & Celery
# --------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379").rstrip("/")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

CELERY_BROKER_URL = f"{REDIS_URL}/1"
CELERY_RESULT_BACKEND = f"{REDIS_URL}/2"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# --------------------------------------------------------------------------
# S3-compatible storage (MinIO in dev, real S3 in prod)
# --------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="" if DEBUG else env.NOTSET)
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="" if DEBUG else env.NOTSET)
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="" if DEBUG else env.NOTSET)
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")
AWS_S3_URL_PROTOCOL = env("AWS_S3_URL_PROTOCOL", default="https:")

if AWS_STORAGE_BUCKET_NAME:
    _default_storage: dict = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {"location": "media"},
    }
else:
    _default_storage = {"BACKEND": "django.core.files.storage.FileSystemStorage"}

STORAGES = {
    "default": _default_storage,
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    MEDIA_URL = "/media/"

# --------------------------------------------------------------------------
# Email — console in dev, Anymail/Postmark in prod (see production.py)
# --------------------------------------------------------------------------
globals().update(env.email_url(
    "EMAIL_URL",
    default="consolemail://" if DEBUG else env.NOTSET,
))

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost" if DEBUG else env.NOTSET)
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

ADMINS = [(e.split("@")[0], e) for e in env.list("DJANGO_ADMINS", default=[])]
MANAGERS = ADMINS

ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": env("POSTMARK_SERVER_TOKEN", default="" if DEBUG else env.NOTSET),
    "WEBHOOK_SECRET": env("ANYMAIL_WEBHOOK_SECRET", default="" if DEBUG else env.NOTSET),
}

# --------------------------------------------------------------------------
# django-mail-auth
# --------------------------------------------------------------------------
LOGIN_URL = "mailauth:login"
LOGIN_REDIRECT_URL = "/"

# --------------------------------------------------------------------------
# django-axes
# --------------------------------------------------------------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_RESET_ON_SUCCESS = True

# --------------------------------------------------------------------------
# Error reporting (GlitchTip via sentry-sdk) — active when DSN is set
# --------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    def _scrub_pii(event: dict, hint: object) -> dict:
        request = event.get("request") or {}
        headers = request.get("headers") or {}
        for h in ("Authorization", "Cookie"):
            headers.pop(h, None)
        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=False,
        before_send=_scrub_pii,
        release=env("SENTRY_RELEASE", default=None),
    )

# --------------------------------------------------------------------------
# GA4 analytics measurement ID (rendered in base template)
# --------------------------------------------------------------------------
ANALYTICS_ID = env("ANALYTICS_ID", default="")

# --------------------------------------------------------------------------
# django-stubs-ext monkeypatch (dev-only dep; guarded so prod skips it)
# --------------------------------------------------------------------------
try:
    import django_stubs_ext
except ImportError:
    pass
else:
    django_stubs_ext.monkeypatch()

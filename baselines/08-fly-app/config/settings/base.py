from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-build-only" if DEBUG else env.NOTSET)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@localhost:5432/postgres" if DEBUG else env.NOTSET,
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "mailauth.contrib.admin",  # must precede django.contrib.admin
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
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",  # must be last
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.analytics",
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
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Redis
REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379").rstrip("/")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Celery
CELERY_BROKER_URL = f"{REDIS_URL}/1"
CELERY_RESULT_BACKEND = f"{REDIS_URL}/2"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# S3 / MinIO storage
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
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

if AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    MEDIA_URL = "/media/"

# Email — consolemail in dev; Anymail (Postmark) overrides EMAIL_BACKEND in prod
globals().update(env.email_url("EMAIL_URL", default="consolemail://" if DEBUG else env.NOTSET))
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="webmaster@localhost" if DEBUG else env.NOTSET
)
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
ADMINS = [(e.split("@")[0], e) for e in env.list("DJANGO_ADMINS", default=[])]
MANAGERS = ADMINS

if not DEBUG:
    EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"

ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": env("POSTMARK_SERVER_TOKEN", default="" if DEBUG else env.NOTSET),
    "WEBHOOK_SECRET": env("ANYMAIL_WEBHOOK_SECRET", default="" if DEBUG else env.NOTSET),
}

# django-mail-auth — AxesBackend must be first
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "mailauth.backends.MailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "mailauth:login"
LOGIN_REDIRECT_URL = "/"

# django-axes
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_RESET_ON_SUCCESS = True

# Analytics (GA4)
ANALYTICS_ID = env("ANALYTICS_ID", default="")
ANALYTICS_HOST = env("ANALYTICS_HOST", default="")

# django-stubs monkeypatch — dev dep only; skipped in the prod image
try:
    import django_stubs_ext
except ImportError:
    pass
else:
    django_stubs_ext.monkeypatch()

from pathlib import Path

import environ
import structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-build-only" if DEBUG else env.NOTSET)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
DATABASES = {
    "default": env.db(
        "DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}" if DEBUG else env.NOTSET
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_rq",
    "django_tasks_rq",
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
]

# Insert CorsMiddleware above CommonMiddleware
common_idx = MIDDLEWARE.index("django.middleware.common.CommonMiddleware")
MIDDLEWARE.insert(common_idx, "corsheaders.middleware.CorsMiddleware")

# Insert RequestContextMiddleware after AuthenticationMiddleware
auth_idx = MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware")
MIDDLEWARE.insert(auth_idx + 1, "config.middleware.logging.RequestContextMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
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

# --- Redis ---
REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379").rstrip("/")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# --- Django Tasks (RQ backend) ---
TASKS = {
    "default": {
        "BACKEND": "django_tasks_rq.RQBackend",
        "QUEUES": ["default"],
    }
}

RQ_QUEUES = {
    "default": {"URL": f"{REDIS_URL}/3"},
}

RQ = {"JOB_CLASS": "django_tasks_rq.Job"}

# --- S3 / MinIO Storage ---
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="" if DEBUG else env.NOTSET)
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="" if DEBUG else env.NOTSET)
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="" if DEBUG else env.NOTSET)
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")

if AWS_STORAGE_BUCKET_NAME:
    _default_storage = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {"location": "media"},
    }
else:
    _default_storage = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }

STORAGES = {
    "default": _default_storage,
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

AWS_S3_URL_PROTOCOL = env("AWS_S3_URL_PROTOCOL", default="https:")
if AWS_S3_CUSTOM_DOMAIN:
    MEDIA_URL = f"{AWS_S3_URL_PROTOCOL}//{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    MEDIA_URL = "/media/"

# --- Email ---
globals().update(
    env.email_url(
        "EMAIL_URL",
        default="consolemail://" if DEBUG else env.NOTSET,
    )
)

DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="webmaster@localhost" if DEBUG else env.NOTSET
)
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
ADMINS = [(email.split("@")[0], email) for email in env.list("DJANGO_ADMINS", default=[])]
MANAGERS = ADMINS

# --- CORS ---
CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"] if DEBUG else [],
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:3000"] if DEBUG else [],
)

# --- Structlog ---
PRE_CHAIN = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": PRE_CHAIN,
        },
        "console": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": PRE_CHAIN,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console" if DEBUG else "json",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {"level": "WARNING"},
        "django.request": {"level": "WARNING"},
        "urllib3": {"level": "WARNING"},
        "botocore": {"level": "WARNING"},
    },
}

structlog.configure(
    processors=[*PRE_CHAIN, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

try:
    import django_stubs_ext
except ImportError:
    pass
else:
    django_stubs_ext.monkeypatch()

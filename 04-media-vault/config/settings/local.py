import os

import structlog

from .base import *  # noqa: F401, F403

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-local-dev-only-do-not-use-in-production"
)

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Postgres in Docker
DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5433"),
        "NAME": os.environ.get("DB_NAME", "media_vault"),
        "USER": os.environ.get("DB_USER", "media_vault"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "media_vault"),
    }
}

# Redis
_redis_host = os.environ.get("REDIS_HOST", "127.0.0.1")
_redis_port = int(os.environ.get("REDIS_PORT", "6379"))

CHANNEL_LAYERS = {  # noqa: F405
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(_redis_host, _redis_port)]},
    }
}

RQ_QUEUES = {  # noqa: F405
    "default": {
        "HOST": _redis_host,
        "PORT": _redis_port,
        "DB": 0,
    }
}

# MinIO (S3-compatible) local
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "media-vault")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", "http://127.0.0.1:9000")
AWS_S3_REGION_NAME = "us-east-1"

# structlog — pretty in dev
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.dev.set_exc_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(10),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

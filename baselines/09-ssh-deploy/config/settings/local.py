import logging

import structlog

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django_structlog": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# Relax CSP in local development
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "blob:"],
    }
}

# Suppress missing staticfiles manifest errors locally
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

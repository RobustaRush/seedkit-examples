import logging
import os
from pathlib import Path

import structlog
from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=[])

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "axes",
    "django_tasks",
    "django_tasks_db",
    "health_check",
    "whitenoise.runserver_nostatic",
]

LOCAL_APPS = [
    "users",
    "jobs",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "axes.middleware.AxesMiddleware",
    "csp.middleware.CSPMiddleware",
    "config.middleware.RequestIdMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 20},
    },
    "cache": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "cache.sqlite3",
        "OPTIONS": {"timeout": 20},
    },
}
DATABASE_ROUTERS = ["config.routers.CacheRouter"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "app_cache",
        "OPTIONS": {"DATABASE": "cache"},
    }
}

# Auth
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Allauth
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# MFA
MFA_TOTP_ISSUER = env.str("MFA_TOTP_ISSUER", default="vps-sqlite-saas")

# Axes
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_RESET_ON_SUCCESS = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Static / media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": str(BASE_DIR / "media"),
            "base_url": "/media/",
        },
    },
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django Tasks
TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.backend.DatabaseBackend",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email (overridden per environment)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="noreply@example.com")
SERVER_EMAIL = env.str("SERVER_EMAIL", default="errors@example.com")
ADMINS = [
    (name, addr)
    for entry in env.list("DJANGO_ADMINS", default=[])
    for name, addr in [entry.split(":", 1)]
]

# CSP (permissive defaults; tighten in production.py)
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_SCRIPT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)

# Structlog (configured here; each env can re-call structlog.configure)
_LOG_LEVEL = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(_LOG_LEVEL),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "axes": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

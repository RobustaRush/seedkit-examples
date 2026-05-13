from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Silk: enable Python profiler in addition to SQL profiling
SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION = False
SILKY_AUTHORISATION = False

# django-zeal: detect N+1 queries in development only
MIDDLEWARE = MIDDLEWARE + [  # noqa: F405
    "zeal.middleware.zeal_middleware",
]

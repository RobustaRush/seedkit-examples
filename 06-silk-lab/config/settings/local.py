from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS = [
    *INSTALLED_APPS,
    "silk",
    "django_extensions",
    "django_migration_linter",
    "zeal",
]

sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
MIDDLEWARE = [
    *MIDDLEWARE[: sec_idx + 1],
    "silk.middleware.SilkyMiddleware",
    *MIDDLEWARE[sec_idx + 1 :],
    "zeal.middleware.zeal_middleware",
]

ZEAL_RAISE_ON_VIOLATION = True

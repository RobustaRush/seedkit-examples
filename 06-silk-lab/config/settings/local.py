from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS = [
    *INSTALLED_APPS,
    "silk",
    "zeal",
    "django_migration_linter",
    "django_extensions",
]

sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
MIDDLEWARE.insert(sec_idx + 1, "silk.middleware.SilkyMiddleware")
MIDDLEWARE += ["zeal.middleware.zeal_middleware"]

ZEAL_RAISE_ON_VIOLATION = True

SILKY_MAX_RECORDED_REQUESTS = 1000
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10

from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

INSTALLED_APPS = [*INSTALLED_APPS, "silk", "zeal", "django_extensions", "django_migration_linter"]

sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
MIDDLEWARE = [
    *MIDDLEWARE[: sec_idx + 1],
    "silk.middleware.SilkyMiddleware",
    "zeal.middleware.zeal_middleware",
    *MIDDLEWARE[sec_idx + 1 :],
]

ZEAL_RAISE_ON_VIOLATION = True

SILKY_MAX_RECORDED_REQUESTS = 1000
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10

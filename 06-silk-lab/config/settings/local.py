from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

if DEBUG:
    INSTALLED_APPS += ["silk", "django_extensions", "django_migration_linter", "zeal"]

    sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(sec_idx + 1, "silk.middleware.SilkyMiddleware")
    MIDDLEWARE += ["zeal.middleware.zeal_middleware"]

    SILKY_MAX_RECORDED_REQUESTS = 1000
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10

    ZEAL_RAISE_ON_VIOLATION = True

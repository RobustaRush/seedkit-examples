from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

if DEBUG:
    INSTALLED_APPS += ["silk"]
    sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(sec_idx + 1, "silk.middleware.SilkyMiddleware")

    SILKY_MAX_RECORDED_REQUESTS = 1000
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10

    INSTALLED_APPS += ["django_extensions"]
    INSTALLED_APPS += ["zeal"]
    MIDDLEWARE += ["zeal.middleware.zeal_middleware"]
    ZEAL_RAISE_ON_VIOLATION = True

    INSTALLED_APPS += ["django_migration_linter"]

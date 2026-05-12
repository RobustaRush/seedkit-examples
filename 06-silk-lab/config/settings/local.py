from .base import *
from .base import INSTALLED_APPS, MIDDLEWARE

if DEBUG:
    INSTALLED_APPS += ["silk"]
    sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(sec_idx + 1, "silk.middleware.SilkyMiddleware")
    MIDDLEWARE += ["zeal.middleware.zeal_middleware"]
    INSTALLED_APPS += ["zeal"]
    INSTALLED_APPS += ["django_migration_linter"]
    INSTALLED_APPS += ["django_extensions"]
    ZEAL_RAISE_ON_VIOLATION = True
    SILKY_MAX_RECORDED_REQUESTS = 1000
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10

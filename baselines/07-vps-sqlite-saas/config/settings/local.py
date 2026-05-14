import structlog

from .base import *  # noqa: F401, F403
from .base import BASE_DIR, env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]

# Disable mandatory email verification locally so login is frictionless
ACCOUNT_EMAIL_VERIFICATION = "optional"

# Console email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Django debug toolbar / internal IPs (optional, uncomment to add)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]

# Reconfigure structlog for pretty dev output
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(10),  # DEBUG
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

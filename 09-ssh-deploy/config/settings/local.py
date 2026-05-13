import structlog

from .base import *  # noqa: F401, F403
from .base import LOGGING, _STRUCTLOG_SHARED

DEBUG = True

# Switch to pretty console renderer in local dev
structlog.configure(
    processors=_STRUCTLOG_SHARED
    + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

LOGGING["handlers"]["console"]["formatter"] = "console"

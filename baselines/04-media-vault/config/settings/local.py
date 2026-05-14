from .base import *  # noqa: F401, F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Override structlog formatter to pretty-print in dev
import structlog  # noqa: E402

LOGGING["handlers"]["console"]["formatter"] = "plain_console"  # type: ignore[name-defined]  # noqa: F405

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# MinIO (S3-compatible) — mirrors the docker-compose minio service
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="minioadmin")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="minioadmin")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="media-vault")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://localhost:9000")
AWS_S3_REGION_NAME = "us-east-1"
AWS_QUERYSTRING_AUTH = True

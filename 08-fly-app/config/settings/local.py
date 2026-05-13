from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Override S3 for local MinIO
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://localhost:9002")  # noqa: F405
AWS_S3_CUSTOM_DOMAIN = None

CONTENT_SECURITY_POLICY = {  # noqa: F811
    "DIRECTIVES": {
        "default-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'unsafe-inline'", "https://www.googletagmanager.com"],
        "img-src": ["'self'", "data:", "http://localhost:9002"],
        "connect-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "font-src": ["'self'"],
    }
}

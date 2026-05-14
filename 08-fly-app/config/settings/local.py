from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {"default": env.db("DATABASE_URL", default="postgres://postgres:postgres@127.0.0.1:5433/08_fly_app")}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AXES_HANDLER = "axes.handlers.database.AxesDatabaseHandler"

CONTENT_SECURITY_POLICY = {  # type: ignore[assignment]
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'", "'unsafe-inline'"),
        "style-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:"),
        "connect-src": ("'self'",),
        "frame-ancestors": ("'none'",),
    },
}

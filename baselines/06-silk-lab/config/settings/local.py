from pathlib import Path

import environ

# Read .env before base.py executes its env() calls.
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(_BASE_DIR / ".env")

from .base import *  # noqa: E402, F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Capture every request with Silk in local dev.
SILKY_PYTHON_PROFILER = True
SILKY_INTERCEPT_PERCENT = 100

# Raise on N+1 queries detected by django-zeal.
ZEAL_RAISE = False  # flip to True when actively hunting N+1s

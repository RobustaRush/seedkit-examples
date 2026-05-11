from .base import *

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

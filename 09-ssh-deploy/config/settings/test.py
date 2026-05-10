from .base import *  # noqa: F401, F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}

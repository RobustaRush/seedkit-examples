from .base import *

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}

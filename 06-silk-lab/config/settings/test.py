from .base import *

DEBUG = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}

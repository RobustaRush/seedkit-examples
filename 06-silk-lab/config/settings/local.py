from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS += ["zeal", "django_migration_linter"]  # noqa: F405
MIDDLEWARE += ["zeal.middleware.zeal_middleware"]  # noqa: F405
ZEAL_RAISE_ON_VIOLATION = True

MIGRATION_LINTER_OPTIONS = {
    "exclude_apps": ["silk", "django_tasks_database"],
}

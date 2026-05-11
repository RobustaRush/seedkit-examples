class CacheRouter:
    """Route django.core.cache reads/writes/migrations to the `cache` database."""

    label = "django_cache"

    def db_for_read(self, model, **hints):
        return "cache" if model._meta.app_label == self.label else None

    def db_for_write(self, model, **hints):
        return "cache" if model._meta.app_label == self.label else None

    def allow_migrate(self, db, app_label, **hints):
        if app_label == self.label:
            return db == "cache"
        return None

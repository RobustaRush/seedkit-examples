class CacheRouter:
    """Prevent regular app migrations from running against the cache database."""

    def db_for_read(self, model, **hints):  # type: ignore[no-untyped-def]
        return None  # DatabaseCache selects its DB via CACHES OPTIONS["DATABASE"]

    def db_for_write(self, model, **hints):  # type: ignore[no-untyped-def]
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):  # type: ignore[no-untyped-def]
        if db == "cache":
            return False
        return None

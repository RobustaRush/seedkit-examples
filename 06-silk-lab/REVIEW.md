## Audit findings

**1. `django-zeal` is installed but never enabled — N+1 detection is silently a no-op.**

`config/settings/local.py` adds `"zeal"` to `INSTALLED_APPS` and sets `ZEAL_RAISE_ON_VIOLATION = True`, but `MIDDLEWARE` only gets `"silk.middleware.SilkyMiddleware"` inserted — there is no `zeal.middleware.ZealMiddleware`. Without it, zeal performs no detection on requests, contradicting the README line `- **django-zeal** — N+1 detection (dev only)`.

Quoted from `config/settings/local.py`:
```
INSTALLED_APPS = [*INSTALLED_APPS, "silk", "zeal", "django_extensions", "django_migration_linter"]
...
    "silk.middleware.SilkyMiddleware",
...
ZEAL_RAISE_ON_VIOLATION = True
```

No other issues found that block boot, fail a smoke check, or constitute a security hole.

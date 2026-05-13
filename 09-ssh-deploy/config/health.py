from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse


def healthz(request):
    """Liveness probe — always returns ok."""
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    """Readiness probe — verifies DB and Redis are reachable."""
    try:
        connection.ensure_connection()
        cache.get("_readyz_probe")
    except Exception:
        return HttpResponse("not ready", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")

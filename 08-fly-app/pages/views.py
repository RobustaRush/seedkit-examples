from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpRequest, HttpResponse


def liveness(_request: HttpRequest) -> HttpResponse:
    """Process is alive. No external checks — must never block."""
    return HttpResponse("ok", content_type="text/plain")


def readiness(_request: HttpRequest) -> HttpResponse:
    """Process can serve traffic — DB reachable."""
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
    except OperationalError:
        return HttpResponse("db down", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")

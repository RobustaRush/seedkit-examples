from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse


def liveness(_request):  # type: ignore[no-untyped-def]
    return HttpResponse("ok", content_type="text/plain")


def readiness(_request):  # type: ignore[no-untyped-def]
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
    except OperationalError:
        return HttpResponse("db down", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")

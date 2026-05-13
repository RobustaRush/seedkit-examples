from django.db import connection
from django.http import HttpRequest, HttpResponse


def healthz(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


def readyz(request: HttpRequest) -> HttpResponse:
    try:
        connection.ensure_connection()
    except Exception:
        return HttpResponse("db unavailable", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")

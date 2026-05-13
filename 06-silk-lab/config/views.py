from django.db import connection
from django.http import HttpRequest, HttpResponse


def healthz(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


def readyz(request: HttpRequest) -> HttpResponse:
    try:
        connection.ensure_connection()
    except Exception:
        return HttpResponse("not ready", status=503)
    return HttpResponse("ready")

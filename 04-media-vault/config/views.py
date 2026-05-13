from django.db import connection
from django.http import HttpRequest, HttpResponse


def healthz(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


def readyz(request: HttpRequest) -> HttpResponse:
    connection.ensure_connection()
    return HttpResponse("ready", content_type="text/plain")

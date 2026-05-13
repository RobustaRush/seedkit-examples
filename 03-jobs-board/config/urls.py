from django.contrib import admin
from django.http import HttpResponse
from django.db import connection
from django.urls import include, path


def healthz(request):
    return HttpResponse("ok")


def readyz(request):
    try:
        connection.ensure_connection()
    except Exception:
        return HttpResponse("not ready", status=503)
    return HttpResponse("ready")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
]

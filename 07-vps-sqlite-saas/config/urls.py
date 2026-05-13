from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def readyz(request):
    from django.db import connections

    for alias in ("default",):
        conn = connections[alias]
        conn.ensure_connection()
    return HttpResponse("ready", content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
]

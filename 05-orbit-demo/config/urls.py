from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def healthz(request):
    return HttpResponse("ok")


def readyz(request):
    return HttpResponse("ready")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("orbit/", include("orbit.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
]

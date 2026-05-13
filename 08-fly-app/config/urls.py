from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from accounts.views import gdpr_delete_view, gdpr_export_view


def health_view(request):
    return HttpResponse("ok")


def readyz_view(request):
    return HttpResponse("ready")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls")),
    path("anymail/", include("anymail.urls")),
    path("accounts/export/", gdpr_export_view, name="gdpr-export"),
    path("accounts/delete/", gdpr_delete_view, name="gdpr-delete"),
    path("healthz", health_view),
    path("readyz", readyz_view),
]

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from config.views import gdpr_delete, gdpr_export, liveness, readiness

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls", namespace="mailauth")),
    path("anymail/", include("anymail.urls")),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
    path("gdpr/export/", gdpr_export, name="gdpr-export"),
    path("gdpr/delete/", gdpr_delete, name="gdpr-delete"),
]

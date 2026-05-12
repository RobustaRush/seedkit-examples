from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from pages.views import liveness, readiness

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("mailauth.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
]

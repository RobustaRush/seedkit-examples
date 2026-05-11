from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from api.urls import router
from api.views import liveness, readiness

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
    path(router.prefix, include((router.urls, "api"), namespace="api")),
    path("django-rq/", include("django_rq.urls")),
]

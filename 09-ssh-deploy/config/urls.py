from django.contrib import admin
from django.urls import include, path

from config.health import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("django-rq/", include("django_rq.urls")),
    path("healthz", healthz),
    path("readyz", readyz),
]

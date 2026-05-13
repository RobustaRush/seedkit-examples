from django.contrib import admin
from django.urls import include, path

from api.urls import router
from config.views import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    path("readyz", readyz),
    path(router.prefix, include((router.urls, "api"), namespace="api")),
]

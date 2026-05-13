from django.contrib import admin
from django.urls import include, path

from config.views import healthz, readyz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),
    path("healthz", healthz),
    path("readyz", readyz),
]

from django.contrib import admin
from django.urls import include, path
from health_check.views import HealthCheckView

from jobs.views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),
    path(
        "health/",
        HealthCheckView.as_view(checks=["health_check.checks.Database"]),
        name="health",
    ),
    path("", index, name="index"),
]

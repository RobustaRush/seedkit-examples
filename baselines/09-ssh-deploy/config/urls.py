from django.contrib import admin
from django.urls import path
from health_check.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view(checks=[
        "health_check.checks.Database",
        "health_check.checks.Cache",
        "health_check.checks.Storage",
    ])),
]

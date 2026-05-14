from django.contrib import admin
from django.urls import include, path

from health_check.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("mailauth.urls")),
    path("ht/", HealthCheckView.as_view(), name="health-check"),
]

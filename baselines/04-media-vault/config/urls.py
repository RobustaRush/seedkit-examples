from django.contrib import admin
from django.urls import include, path

from health_check.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls", namespace="api")),
    path("ht/", HealthCheckView.as_view(), name="health-check"),
    path("django-rq/", include("django_rq.urls")),
]

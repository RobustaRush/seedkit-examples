from django.contrib import admin
from django.urls import include, path
from health_check.checks import Database, Storage
from health_check.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("ht/", HealthCheckView.as_view(checks=[Database, Storage]), name="health_check"),
]

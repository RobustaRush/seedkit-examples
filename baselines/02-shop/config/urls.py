from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from health_check.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("health/", HealthCheckView.as_view()),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("", include("pages.urls")),
]

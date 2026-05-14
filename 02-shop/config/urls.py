from django.contrib import admin
from django.urls import include, path

from config.health import liveness, readiness
from config.robots import robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", include("pages.urls")),
]

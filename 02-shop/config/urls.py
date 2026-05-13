from django.contrib import admin
from django.urls import include, path

from pages.views import IndexView

from .health import healthz, readyz
from .robots import robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("", IndexView.as_view(), name="index"),
]

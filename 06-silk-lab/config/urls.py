from django.conf import settings
from django.contrib import admin
from django.urls import path

from pages.views import home, liveness, readiness

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
]

if settings.DEBUG:
    from django.urls import include

    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

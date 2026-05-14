from django.contrib import admin
from django.urls import include, path

from app.views import send_test_mail

urlpatterns = [
    path("admin/", admin.site.urls),
    path("orbit/", include("orbit.urls", namespace="orbit")),
    path("send-mail/", send_test_mail, name="send_test_mail"),
]

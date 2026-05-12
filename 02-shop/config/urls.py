from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from billing import views as billing_views
from pages.views import IndexView, liveness, readiness, robots_txt

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("billing/checkout/", billing_views.create_checkout_session, name="billing-checkout"),
    path("billing/portal/", billing_views.customer_portal, name="billing-portal"),
    path("billing/webhook/", billing_views.stripe_webhook, name="stripe-webhook"),
    path("healthz", liveness, name="healthz"),
    path("readyz", readiness, name="readyz"),
    path("robots.txt", robots_txt, name="robots"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

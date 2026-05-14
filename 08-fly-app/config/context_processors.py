from django.conf import settings
from django.http import HttpRequest


def ga4(request: HttpRequest) -> dict:
    return {"GA4_MEASUREMENT_ID": getattr(settings, "GOOGLE_ANALYTICS_MEASUREMENT_ID", "")}

from django.conf import settings
from django.http import HttpRequest


def analytics(request: HttpRequest) -> dict:
    return {
        "ANALYTICS_ID": settings.ANALYTICS_ID,
        "ANALYTICS_HOST": settings.ANALYTICS_HOST,
        "DEBUG": settings.DEBUG,
    }

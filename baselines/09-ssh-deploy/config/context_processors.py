from django.conf import settings


def analytics(request):
    return {
        "UMAMI_WEBSITE_ID": getattr(settings, "UMAMI_WEBSITE_ID", ""),
        "UMAMI_HOST": getattr(settings, "UMAMI_HOST", ""),
    }

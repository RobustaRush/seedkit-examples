from django.conf import settings


def umami(request):
    return {
        "UMAMI_HOST": getattr(settings, "UMAMI_HOST", ""),
        "UMAMI_WEBSITE_ID": getattr(settings, "UMAMI_WEBSITE_ID", ""),
    }

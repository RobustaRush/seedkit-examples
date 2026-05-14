from django.conf import settings


def umami(request):
    return {
        "UMAMI_WEBSITE_ID": getattr(settings, "UMAMI_WEBSITE_ID", ""),
        "UMAMI_URL": getattr(settings, "UMAMI_URL", ""),
    }

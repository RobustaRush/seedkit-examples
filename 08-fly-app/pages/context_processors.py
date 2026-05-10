from django.conf import settings


def analytics(request: object) -> dict:
    return {"ANALYTICS_ID": getattr(settings, "ANALYTICS_ID", "")}

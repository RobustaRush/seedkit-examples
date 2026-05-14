from django.conf import settings


def goatcounter(request):
    return {"GOATCOUNTER_SITE_CODE": getattr(settings, "GOATCOUNTER_SITE_CODE", "")}

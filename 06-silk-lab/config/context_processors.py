from django.conf import settings
from django.http import HttpRequest


def goatcounter(request: HttpRequest) -> dict:
    return {"GOATCOUNTER_URL": getattr(settings, "GOATCOUNTER_URL", "")}

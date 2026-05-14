import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

User = get_user_model()


def liveness(_request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok", content_type="text/plain")


def readiness(_request: HttpRequest) -> HttpResponse:
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
    except OperationalError:
        return HttpResponse("db down", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")


@login_required
def gdpr_export(request: HttpRequest) -> HttpResponse:
    user = request.user
    data = {
        "id": user.pk,
        "username": user.get_username(),
        "email": getattr(user, "email", ""),
        "date_joined": str(getattr(user, "date_joined", "")),
        "last_login": str(getattr(user, "last_login", "")),
    }
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json",
    )
    response["Content-Disposition"] = 'attachment; filename="my-data.json"'
    return response


@login_required
@require_POST
def gdpr_delete(request: HttpRequest) -> HttpResponse:
    user = request.user
    user.delete()
    return HttpResponse("Your account has been deleted.", content_type="text/plain")

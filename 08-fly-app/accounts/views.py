from typing import cast

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


@login_required
def gdpr_export_view(request: HttpRequest) -> JsonResponse:
    user = cast(User, request.user)
    data = {
        "id": user.pk,
        "username": user.username,
        "email": user.email,
        "date_joined": user.date_joined.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }
    response = JsonResponse(data)
    response["Content-Disposition"] = 'attachment; filename="my-data.json"'
    return response


@login_required
@require_POST
def gdpr_delete_view(request: HttpRequest):
    user = cast(User, request.user)
    logout(request)
    user.delete()
    return redirect("/")

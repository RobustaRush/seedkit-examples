import uuid
from collections.abc import Callable

import structlog
from django.http import HttpRequest, HttpResponse


class RequestIdMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=str(uuid.uuid4()))
        return self.get_response(request)

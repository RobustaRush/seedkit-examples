import uuid

import structlog

log = structlog.get_logger(__name__)

_NO_USER_PATHS = ("/healthz", "/readyz")


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        structlog.contextvars.clear_contextvars()
        ctx = {"request_id": request.headers.get("X-Request-ID") or uuid.uuid4().hex}
        if not request.path.startswith(_NO_USER_PATHS):
            ctx["user_id"] = getattr(getattr(request, "user", None), "id", None)
        structlog.contextvars.bind_contextvars(**ctx)
        try:
            response = self.get_response(request)
            log.info("request", method=request.method, path=request.path, status=response.status_code)
            return response
        finally:
            structlog.contextvars.clear_contextvars()

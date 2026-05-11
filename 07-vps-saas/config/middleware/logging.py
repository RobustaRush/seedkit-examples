import time
import uuid

import structlog

log = structlog.get_logger("request")

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
        start = time.monotonic()
        try:
            response = self.get_response(request)
        finally:
            log.info(
                "request",
                method=request.method,
                path=request.path,
                status=getattr(locals().get("response"), "status_code", 0),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
            structlog.contextvars.clear_contextvars()
        return response

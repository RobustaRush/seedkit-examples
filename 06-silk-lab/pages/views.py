from django.conf import settings
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse

if settings.DEBUG:
    from silk.profiling.profiler import silk_profile
else:

    def silk_profile(*_a, **_kw):
        def deco(fn):
            return fn

        return deco


def liveness(_request):
    """Process is alive. No external checks — must never block."""
    return HttpResponse("ok", content_type="text/plain")


def readiness(_request):
    """Process can serve traffic — DB reachable."""
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
    except OperationalError:
        return HttpResponse("db down", status=503, content_type="text/plain")
    return HttpResponse("ready", content_type="text/plain")


@silk_profile(name="home")
def home(_request):
    """Simple home view — profiled with @silk_profile."""
    return HttpResponse(
        "<h1>silk-lab</h1><p>Visit <a href='/silk/'>Silk dashboard</a>.</p>",
        content_type="text/html",
    )

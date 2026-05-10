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


@silk_profile(name="liveness")
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

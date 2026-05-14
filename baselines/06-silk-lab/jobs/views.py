from django.http import HttpResponse
from silk.profiling.profiler import silk_profile


@silk_profile(name="jobs-index")
def index(request):
    return HttpResponse("silk-lab ok\n", content_type="text/plain")

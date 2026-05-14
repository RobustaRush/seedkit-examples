from django.views.generic import ListView

from .models import Job


class JobListView(ListView):
    model = Job
    queryset = Job.objects.filter(is_active=True)
    context_object_name = "jobs"

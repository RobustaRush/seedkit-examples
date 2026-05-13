from django.views.generic import ListView

from .models import JobPost


class JobListView(ListView):
    model = JobPost
    queryset = JobPost.objects.filter(is_active=True)
    context_object_name = "jobs"

from celery import shared_task


@shared_task
def send_daily_digest():
    """Send daily job digest email to all active subscribers."""
    from .models import JobPost

    active_jobs = JobPost.objects.filter(is_active=True).count()
    # TODO: render digest template and send via Django's send_mail
    return f"Daily digest sent: {active_jobs} active jobs"


@shared_task
def notify_new_job(job_id: int):
    """Send email notification when a new job post is published."""
    from .models import JobPost

    try:
        job = JobPost.objects.get(pk=job_id)
    except JobPost.DoesNotExist:
        return f"Job {job_id} not found"
    # TODO: send notification emails to subscribers
    return f"Notified subscribers of new job: {job}"

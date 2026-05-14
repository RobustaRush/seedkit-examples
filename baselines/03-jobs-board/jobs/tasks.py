from celery import shared_task


@shared_task
def send_job_notification(job_id: int) -> str:
    """Send an email notification when a new job is posted."""
    # TODO: fetch Job by job_id, render template, call send_mail
    return f"notification sent for job {job_id}"


@shared_task
def send_daily_digest() -> str:
    """Aggregate today's active jobs and email a digest (scheduled via Beat)."""
    # TODO: query Job.objects.filter(is_active=True, published_at__date=today),
    #       render digest template, call send_mail
    return "daily digest sent"

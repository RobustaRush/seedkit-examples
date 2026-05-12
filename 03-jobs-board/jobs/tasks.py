from celery import shared_task


@shared_task
def send_notification_email(job_id: int, recipient_email: str) -> str:
    """Send a notification email for a new job posting."""
    # Real implementation: render email template and send via Django's mail stack.
    return f"Notification sent for job {job_id} to {recipient_email}"


@shared_task
def send_daily_digest() -> str:
    """Send a daily digest of new job postings. Scheduled via CELERY_BEAT_SCHEDULE."""
    # Real implementation: query recent jobs, render digest, send to subscribers.
    return "Daily digest sent"

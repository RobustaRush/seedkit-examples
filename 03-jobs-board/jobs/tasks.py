from celery import shared_task


@shared_task
def send_daily_digest():
    """Send a daily job digest email to subscribers."""
    # Placeholder: query active job listings and email subscribers.
    return "daily digest sent"

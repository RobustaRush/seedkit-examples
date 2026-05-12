from celery import shared_task


@shared_task
def send_daily_digest():
    """Send a daily digest email of new job listings."""
    # TODO: query new job listings and email subscribers
    return "daily digest sent"

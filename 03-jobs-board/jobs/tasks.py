from celery import shared_task


@shared_task
def send_daily_digest():
    """Send the daily job digest email to subscribers."""
    # TODO: query active Job listings and email subscribers
    return "daily digest sent"

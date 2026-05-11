from celery import shared_task


@shared_task
def send_daily_digest():
    """Send the daily job board digest email to subscribers."""
    # TODO: query jobs posted since yesterday and email subscribers
    return "digest sent"

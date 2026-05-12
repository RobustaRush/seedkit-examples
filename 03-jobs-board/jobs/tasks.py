from celery import shared_task


@shared_task
def send_daily_digest():
    """Send a daily digest email to all subscribers. Called by Celery Beat at 08:00 UTC."""
    # TODO: query Job model, render email, send via Django mail
    pass

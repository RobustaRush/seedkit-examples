from celery import shared_task


@shared_task
def send_daily_digest():
    """Placeholder for the daily job digest email."""
    print("Sending daily digest…")
    return "digest sent"

from celery import shared_task


@shared_task
def send_welcome_email(user_id: int) -> None:
    """Send a welcome email to a newly registered user."""
    pass


@shared_task
def send_daily_digest() -> None:
    """Compile and send the daily job-board digest to all subscribers."""
    pass

from celery import shared_task


@shared_task
def send_notification_email(user_id: int) -> None:
    """Send a background email notification to a user."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return
    send_mail(
        subject="Job board notification",
        message="You have a new notification from the job board.",
        from_email=None,
        recipient_list=[user.email],
    )


@shared_task
def daily_digest() -> None:
    """Send the daily digest email. Scheduled via Celery Beat."""
    from django.core.mail import send_mail

    send_mail(
        subject="Daily job digest",
        message="Here are today's new job listings.",
        from_email=None,
        recipient_list=["digest@example.com"],
    )

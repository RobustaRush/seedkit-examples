from celery import shared_task


@shared_task
def send_notification_email(user_id: int, subject: str, message: str) -> str:
    """Send a one-off notification email to a user (queued via Celery)."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()
    user = User.objects.get(pk=user_id)
    send_mail(subject, message, None, [user.email])
    return f"sent to {user.email}"


@shared_task
def send_daily_digest() -> str:
    """Scheduled by Celery Beat — sends a daily job-board digest email."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail

    User = get_user_model()
    emails = list(User.objects.filter(is_active=True).values_list("email", flat=True))
    if emails:
        send_mail(
            "Daily jobs digest",
            "Here are today's new job listings.",
            None,
            emails,
        )
    return f"digest sent to {len(emails)} users"

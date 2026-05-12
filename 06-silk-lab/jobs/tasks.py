from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task


@task()
def send_welcome_email(to_address: str) -> None:
    """Send a welcome email. Enqueue with: send_welcome_email.enqueue("user@example.com")"""
    send_mail(
        subject="Welcome!",
        message="Thanks for signing up.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_address],
    )

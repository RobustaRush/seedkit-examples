from django.core.mail import send_mail
from django.tasks import task


@task()
def send_welcome_email(to_address: str) -> None:
    """Send a welcome email to the given address."""
    send_mail(
        subject="Welcome to Silk Lab",
        message="Thanks for signing up!",
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=[to_address],
    )

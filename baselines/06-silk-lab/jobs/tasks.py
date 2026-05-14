from django.core.mail import send_mail
from django_tasks import task


@task
def send_welcome_email(to_address: str) -> None:
    """Send a welcome e-mail. Runs in a db_worker process."""
    send_mail(
        subject="Welcome to silk-lab",
        message="Your account is ready.",
        from_email="noreply@example.com",
        recipient_list=[to_address],
    )

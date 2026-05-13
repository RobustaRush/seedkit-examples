from django.core.mail import send_mail
from django_tasks import task


@task()
def send_welcome_email(to_address: str) -> None:
    """Enqueue with: from jobs.tasks import send_welcome_email; send_welcome_email.enqueue("you@example.com")"""
    send_mail(
        subject="Welcome to Silk Lab!",
        message="Thanks for stopping by.",
        from_email="noreply@example.com",
        recipient_list=[to_address],
    )

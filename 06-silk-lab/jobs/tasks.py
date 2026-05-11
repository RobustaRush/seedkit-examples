from django.core.mail import send_mail
from django.tasks import task


@task()
def send_example_email(to: str) -> None:
    """Example background task: send a plain email."""
    send_mail(
        subject="Hello from silk-lab",
        message="This email was sent from a django-tasks background task.",
        from_email=None,
        recipient_list=[to],
    )

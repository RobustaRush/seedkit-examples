from django.core.mail import send_mail
from django_tasks import task


@task()
def send_welcome_email(to_address: str) -> None:
    send_mail(
        subject="Welcome!",
        message="Thanks for signing up.",
        from_email="noreply@example.com",
        recipient_list=[to_address],
    )

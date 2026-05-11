from django.core.mail import send_mail
from django.tasks import task


@task()
def send_welcome_email(to_address: str) -> None:
    send_mail(
        subject="Welcome to Silk Lab",
        message="This email was sent by a background task.",
        from_email=None,
        recipient_list=[to_address],
    )

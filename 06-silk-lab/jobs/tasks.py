import logging

from django.core.mail import send_mail
from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(recipient: str) -> None:
    send_mail(
        subject="Welcome to Silk Lab",
        message="Thanks for signing up.",
        from_email=None,
        recipient_list=[recipient],
    )
    logger.info("Welcome email sent to %s", recipient)

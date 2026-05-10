import logging

from django.core.mail import send_mail
from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(user_id: int) -> None:
    logger.info("send_welcome_email started", extra={"user_id": user_id})
    send_mail(
        subject="Welcome!",
        message=f"Welcome, user {user_id}!",
        from_email="noreply@example.com",
        recipient_list=[f"user-{user_id}@example.com"],
    )
    logger.info("send_welcome_email finished", extra={"user_id": user_id})

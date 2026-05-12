import logging

from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(user_id: int) -> None:
    """Sample background task — replace with real work."""
    logger.info("send_welcome_email", extra={"user_id": user_id})

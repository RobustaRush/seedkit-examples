import logging

from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(user_pk: int) -> None:
    """Sample task — replace with real work."""
    logger.info("send_welcome_email called", extra={"user_pk": user_pk})

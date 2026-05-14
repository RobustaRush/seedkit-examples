import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def send_welcome_email(user_id: int) -> None:
    logger.info("send_welcome_email.start", user_id=user_id)
    # TODO: replace with real email logic
    logger.info("send_welcome_email.done", user_id=user_id)

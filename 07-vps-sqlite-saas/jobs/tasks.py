import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def send_welcome_email(user_id: int) -> None:
    logger.info("send_welcome_email.start", user_id=user_id)
    # TODO: load user and send email
    logger.info("send_welcome_email.done", user_id=user_id)

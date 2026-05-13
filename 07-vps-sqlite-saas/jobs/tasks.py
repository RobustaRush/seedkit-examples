import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def send_welcome_email(user_pk: int) -> None:
    from users.models import User

    user = User.objects.get(pk=user_pk)
    logger.info("send_welcome_email", user_id=user_pk, email=user.email)
    # TODO: replace with real email sending

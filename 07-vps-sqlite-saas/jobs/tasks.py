import logging

from django_tasks import task

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(user_id: int) -> None:
    """Sample task — send a welcome email to the newly registered user."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("send_welcome_email: user %s not found", user_id)
        return
    logger.info("Sending welcome email to %s", getattr(user, "email", str(user)))

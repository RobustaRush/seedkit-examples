from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django_tasks import task

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@task()
def send_welcome_email(user_id: int) -> None:
    """Sample background task — send a welcome email to a newly registered user."""
    from users.models import User

    user = User.objects.get(pk=user_id)
    logger.info("Sending welcome email", extra={"user_id": user_id, "email": user.email})
    # TODO: replace with real email logic

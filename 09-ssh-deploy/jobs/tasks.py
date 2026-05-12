import logging

from django.tasks import task

logger = logging.getLogger(__name__)


@task
def sample_task(message: str) -> str:
    """Sample background task. Replace with real work."""
    logger.info("sample_task running", extra={"message": message})
    return f"processed: {message}"

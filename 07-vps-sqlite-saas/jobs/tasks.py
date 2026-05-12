import logging

from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def example_task(message: str) -> str:
    """Sample background task. Enqueue with: example_task.enqueue("hello")"""
    logger.info("example_task running", extra={"message": message})
    return f"done: {message}"

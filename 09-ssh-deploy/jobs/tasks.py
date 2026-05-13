import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def sample_task(message: str) -> str:
    """A sample background task — enqueue with sample_task.enqueue(message='hello')."""
    logger.info("sample_task.run", message=message)
    return f"processed: {message}"

import structlog
from django.tasks import task

logger = structlog.get_logger(__name__)


@task()
def sample_task(message: str) -> str:
    logger.info("sample_task.run", message=message)
    return f"done: {message}"

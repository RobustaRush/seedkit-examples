import structlog
from django.tasks import task

logger = structlog.get_logger(__name__)


@task()
def sample_task(message: str) -> str:
    logger.info("sample_task.start", message=message)
    result = f"processed: {message}"
    logger.info("sample_task.done", result=result)
    return result

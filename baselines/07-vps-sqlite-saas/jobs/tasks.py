import structlog
from django_tasks import task

log = structlog.get_logger(__name__)


@task()
def sample_task(message: str) -> str:
    """Example background task — enqueue with sample_task.enqueue("hello")."""
    log.info("sample_task.started", message=message)
    result = f"processed: {message}"
    log.info("sample_task.finished", result=result)
    return result

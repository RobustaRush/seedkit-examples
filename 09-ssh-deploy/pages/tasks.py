import structlog
from django.tasks import task

log = structlog.get_logger(__name__)


@task
def sample_task(message: str) -> None:
    log.info("sample_task.run", message=message)

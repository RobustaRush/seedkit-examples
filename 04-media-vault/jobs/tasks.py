import structlog
from django.tasks import task

log = structlog.get_logger(__name__)


@task()
def process_upload(filename: str, size: int) -> None:
    log.info("processing_upload", filename=filename, size=size)

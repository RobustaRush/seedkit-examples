import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def process_upload(file_uid: str) -> None:
    logger.info("processing_upload", file_uid=file_uid)

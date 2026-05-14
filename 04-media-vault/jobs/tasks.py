import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def process_media(uid: str, filename: str) -> None:
    logger.info("processing_media", uid=uid, filename=filename)

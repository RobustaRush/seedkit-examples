import structlog
from django.tasks import task

log = structlog.get_logger(__name__)


@task()
def process_media(media_uid: str) -> None:
    log.info("processing_media", uid=media_uid)

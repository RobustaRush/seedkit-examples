import structlog
from django_tasks import task

log = structlog.get_logger(__name__)


@task()
def process_media(media_uid: str, filename: str) -> None:
    log.info("processing_media", uid=media_uid, filename=filename)
    # placeholder: do transcoding / thumbnail / virus-scan here
    log.info("media_processed", uid=media_uid)

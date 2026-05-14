import structlog
from django_tasks import task

log = structlog.get_logger(__name__)


@task()
def process_upload(media_uid: str, filename: str) -> None:
    """Simulate post-upload processing (thumbnail, virus scan, metadata extraction)."""
    log.info("process_upload.started", media_uid=media_uid, filename=filename)
    # TODO: replace with real processing steps
    log.info("process_upload.finished", media_uid=media_uid)

import logging

from django.tasks import task

logger = logging.getLogger(__name__)


@task
def process_upload(filename: str, size: int) -> None:
    """Sample background task: simulate processing an uploaded file."""
    logger.info("processing_upload", extra={"filename": filename, "size": size})

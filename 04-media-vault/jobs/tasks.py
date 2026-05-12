import logging

from django.tasks import task

logger = logging.getLogger(__name__)


@task()
def process_upload(filename: str, size: int) -> dict[str, str | int]:
    """Sample background task: log upload details and return a summary."""
    logger.info("processing_upload", extra={"filename": filename, "size": size})
    return {"filename": filename, "size": size, "status": "processed"}

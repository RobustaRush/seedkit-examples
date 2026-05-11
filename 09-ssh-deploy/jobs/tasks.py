import structlog
from django.tasks import task

logger = structlog.get_logger(__name__)


@task()
def process_message(message: str) -> str:
    """Sample background task — enqueue with process_message.enqueue("hello")."""
    logger.info("processing_message", message=message)
    result = f"Processed: {message}"
    logger.info("message_processed", result=result)
    return result

import structlog
from django_tasks import task

logger = structlog.get_logger(__name__)


@task()
def process_job(job_id: int) -> str:
    """Sample background task — replace with real business logic."""
    logger.info("job.started", job_id=job_id)
    result = f"Processed job {job_id}"
    logger.info("job.completed", job_id=job_id, result=result)
    return result

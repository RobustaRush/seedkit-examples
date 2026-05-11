from celery import shared_task


@shared_task
def send_application_notification(job_id: int, applicant_email: str) -> str:
    """Send email notification when someone applies to a job listing."""
    # TODO: implement real email via Django's send_mail
    return f"notification sent for job {job_id} to {applicant_email}"


@shared_task
def daily_digest() -> str:
    """Send daily digest of new job listings — scheduled by Celery Beat."""
    # TODO: query new listings and send digest email
    return "daily digest sent"

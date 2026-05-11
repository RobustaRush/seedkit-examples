from celery import shared_task


@shared_task
def example_task() -> str:
    return "done"

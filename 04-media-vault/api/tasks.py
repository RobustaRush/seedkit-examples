from django.tasks import task


@task()
def process_media(uid: str) -> None:
    import structlog

    log = structlog.get_logger(__name__)
    log.info("processing media", uid=uid)

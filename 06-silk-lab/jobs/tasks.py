import logging

from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task

logger = logging.getLogger(__name__)

if settings.DEBUG:
    from silk.profiling.profiler import silk_profile
else:

    class silk_profile:
        def __init__(self, *_a, **_kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def __call__(self, fn):
            return fn


@task()
def send_welcome_email(to_address: str) -> None:
    """Send a welcome email. Enqueue with: send_welcome_email.enqueue('user@example.com')"""
    with silk_profile(name="send_welcome_email"):
        logger.info("Sending welcome email to %s", to_address)
        send_mail(
            subject="Welcome!",
            message="Thanks for joining.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_address],
        )
        logger.info("Welcome email sent to %s", to_address)

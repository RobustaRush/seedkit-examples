from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task

if settings.DEBUG:
    from silk.profiling.profiler import silk_profile
else:

    class silk_profile:
        def __init__(self, *_a, **_kw):
            pass

        def __call__(self, fn):
            return fn

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False


@task()
def send_welcome_email(to_address: str) -> None:
    """Send a welcome email. Enqueue with: send_welcome_email.enqueue('user@example.com')"""
    with silk_profile(name="send_welcome_email"):
        send_mail(
            subject="Welcome!",
            message="Thanks for signing up.",
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[to_address],
        )

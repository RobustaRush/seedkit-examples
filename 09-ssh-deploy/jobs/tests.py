import pytest


@pytest.mark.django_db
def test_sample_task_no_email():
    """Verifies email add-on was deliberately skipped."""
    from django.conf import settings

    assert (
        not hasattr(settings, "EMAIL_HOST")
        or settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"
    )

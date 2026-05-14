"""Verify the project does not send transactional email (dummy backend)."""
import django.test
import pytest
from django.core import mail
from django.test import override_settings


def test_email_backend_setting():
    """Base settings configure the dummy backend (no transactional mail)."""
    from django.conf import settings as django_settings

    # Read directly from the module, bypassing pytest-django's locmem override
    import config.settings.base as base_settings

    assert base_settings.EMAIL_BACKEND == "django.core.mail.backends.dummy.EmailBackend"


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND="django.core.mail.backends.dummy.EmailBackend")
def test_dummy_backend_does_not_populate_outbox():
    """Dummy backend swallows all mail silently."""
    from django.core.mail import send_mail

    send_mail("Subject", "Body", "from@example.com", ["to@example.com"])
    assert len(mail.outbox) == 0

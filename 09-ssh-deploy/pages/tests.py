import pytest


@pytest.mark.django_db
def test_liveness(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_readiness(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.content == b"ready"


def test_no_email_backend():
    """Verify transactional email was deliberately skipped — no EMAIL_BACKEND that sends."""
    from django.conf import settings

    backend = getattr(settings, "EMAIL_BACKEND", "django.core.mail.backends.locmem.EmailBackend")
    assert "smtp" not in backend.lower(), "smtp email backend should not be configured"
    assert "anymail" not in backend.lower(), "anymail should not be configured"

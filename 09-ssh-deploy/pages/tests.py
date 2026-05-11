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


def test_email_not_configured():
    """Verify this project deliberately skips email configuration."""
    from django.conf import settings

    assert not hasattr(settings, "EMAIL_URL"), (
        "09-ssh-deploy does not send transactional mail; EMAIL_URL must not be set"
    )

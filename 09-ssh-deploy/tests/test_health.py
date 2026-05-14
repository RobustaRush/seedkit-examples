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


def test_no_smtp_configured(settings):
    # This project sends no transactional mail — assert no SMTP backend is wired up.
    backend = getattr(settings, "EMAIL_BACKEND", "django.core.mail.backends.dummy.EmailBackend")
    assert "smtp" not in backend.lower()

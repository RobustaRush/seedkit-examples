import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


def test_liveness(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_readiness(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.content == b"ready"


def test_email_backend_is_locmem():
    from django.conf import settings

    assert "locmem" in settings.EMAIL_BACKEND

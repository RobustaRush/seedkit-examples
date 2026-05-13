import pytest


@pytest.mark.django_db
def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_readyz(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.content == b"ready"

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

import pytest


@pytest.mark.django_db
def test_healthz(client):
    assert client.get("/healthz").status_code == 200


@pytest.mark.django_db
def test_readyz(client):
    assert client.get("/readyz").status_code == 200

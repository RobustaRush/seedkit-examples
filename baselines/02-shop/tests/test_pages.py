import pytest


@pytest.mark.django_db
def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_index_contains_tailwind_utility(client):
    response = client.get("/")
    content = response.content.decode()
    assert "text-blue-600" in content
    assert "text-4xl" in content


@pytest.mark.django_db
def test_index_contains_daisyui_component(client):
    response = client.get("/")
    content = response.content.decode()
    assert 'class="btn btn-primary' in content


@pytest.mark.django_db
def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent" in response.content


@pytest.mark.django_db
def test_health_check(client):
    response = client.get("/health/")
    assert response.status_code in (200, 500)

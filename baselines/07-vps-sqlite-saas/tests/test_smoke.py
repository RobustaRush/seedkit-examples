import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_health_check(client: Client) -> None:
    response = client.get("/ht/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_redirect(client: Client) -> None:
    response = client.get("/admin/", follow=False)
    assert response.status_code in (200, 302)


def test_sample_task_importable() -> None:
    from jobs.tasks import sample_task

    assert callable(sample_task.enqueue)

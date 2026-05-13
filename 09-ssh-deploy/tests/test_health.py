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


def test_email_not_smtp(settings):
    """Verify SMTP is not configured — project does not send transactional mail."""
    assert settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend"


def test_tasks_importable():
    """Verify the tasks module loads without error."""
    from jobs.tasks import sample_task  # noqa: F401

    assert callable(sample_task.enqueue)

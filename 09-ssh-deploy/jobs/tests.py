import pytest


@pytest.mark.django_db
def test_sample_task_runs():
    from jobs.tasks import sample_task

    result = sample_task.enqueue("test")
    assert result is not None

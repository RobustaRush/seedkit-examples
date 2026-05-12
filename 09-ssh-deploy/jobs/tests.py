import pytest

from jobs.tasks import sample_task


@pytest.mark.django_db
def test_sample_task():
    result = sample_task.enqueue("hello")
    assert result is not None

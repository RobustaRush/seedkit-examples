import pytest


@pytest.mark.django_db
def test_process_message():
    from jobs.tasks import process_message

    result = process_message.enqueue("hello")
    assert result.return_value == "Processed: hello"

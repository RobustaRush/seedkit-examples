import pytest


@pytest.mark.django_db
def test_db_available(db):
    from django.contrib.auth.models import User
    assert User.objects.count() == 0

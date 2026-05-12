import pytest

from users.models import User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="user@example.com", password="secret")
    assert user.email == "user@example.com"
    assert user.is_staff is False


@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(email="admin@example.com", password="secret")
    assert user.is_staff is True
    assert user.is_superuser is True

import pytest


@pytest.mark.django_db
def test_create_user():
    from users.models import User

    user = User.objects.create_user(email="test@example.com", password="testpass123")
    assert user.email == "test@example.com"
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_superuser():
    from users.models import User

    user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
    assert user.is_staff
    assert user.is_superuser

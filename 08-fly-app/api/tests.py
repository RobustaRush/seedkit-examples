import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_api_module_loads():
    from api.api import api, get_user
    assert api is not None
    assert get_user is not None


@pytest.mark.django_db
def test_user_schema():
    from api.api import UserSchema
    user = User.objects.create_user(username="alice", email="alice@example.com")
    schema = UserSchema(id=user.pk, username=user.username)
    assert schema.username == "alice"

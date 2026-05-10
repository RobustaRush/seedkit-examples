import msgspec
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI

User = get_user_model()
api = BoltAPI()


class UserSchema(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserSchema:
    user = await User.objects.aget(id=user_id)
    return UserSchema(id=user.id, username=user.username)  # type: ignore[attr-defined]

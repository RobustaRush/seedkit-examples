import msgspec
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException

User = get_user_model()

api = BoltAPI()


class UserOut(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(user_id: int) -> UserOut:
    try:
        user = await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found") from None
    return UserOut(id=user.pk, username=user.get_username())

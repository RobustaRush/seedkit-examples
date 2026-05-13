import msgspec
from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException
from django_bolt.status_codes import HTTP_404_NOT_FOUND

from django.contrib.auth.models import User

api = BoltAPI()


class UserResponse(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(request, user_id: int) -> UserResponse:
    try:
        user = await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(id=user.pk, username=user.username)

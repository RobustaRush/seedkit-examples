import msgspec
from django.contrib.auth import get_user_model
from django_bolt import BoltAPI, Request, Response

User = get_user_model()

api = BoltAPI()


class UserOut(msgspec.Struct):
    id: int
    username: str


@api.get("/users/{user_id}")
async def get_user(request: Request, user_id: int):
    try:
        user = await User.objects.aget(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "not found"}, status_code=404)
    return UserOut(id=user.pk, username=user.get_username())

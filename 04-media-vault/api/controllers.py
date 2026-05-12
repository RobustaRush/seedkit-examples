import uuid

from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer

from .schemas import MediaCreate, MediaResponse


class MediaController(Controller[MsgspecSerializer]):
    async def post(self, parsed_body: Body[MediaCreate]) -> MediaResponse:
        return MediaResponse(uid=uuid.uuid4(), filename=parsed_body.filename)

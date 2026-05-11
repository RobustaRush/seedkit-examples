import uuid

import msgspec
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer


class MediaCreate(msgspec.Struct):
    filename: str
    size: int


class MediaResponse(msgspec.Struct):
    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    async def post(self, parsed_body: Body[MediaCreate]) -> MediaResponse:
        return MediaResponse(uid=uuid.uuid4(), filename=parsed_body.filename)

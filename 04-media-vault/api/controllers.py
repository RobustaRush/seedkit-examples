import uuid

import msgspec
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer


class MediaUpload(msgspec.Struct):
    filename: str
    size: int


class MediaResponse(msgspec.Struct):
    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    async def post(self, parsed_body: Body[MediaUpload]) -> MediaResponse:
        return MediaResponse(uid=uuid.uuid4(), filename=parsed_body.filename)

import uuid

import msgspec
from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer


class MediaIn(msgspec.Struct):
    filename: str
    size: int


class MediaOut(msgspec.Struct):
    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    def post(self, parsed_body: Body[MediaIn]) -> MediaOut:
        return MediaOut(uid=uuid.uuid4(), filename=parsed_body.filename)

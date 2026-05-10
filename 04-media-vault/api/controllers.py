import uuid

from dmr import Body, Controller
from dmr.plugins.msgspec import MsgspecSerializer

from .schemas import MediaCreate, MediaOut


class MediaController(Controller[MsgspecSerializer]):
    def post(self, parsed_body: Body[MediaCreate]) -> MediaOut:
        return MediaOut(uid=uuid.uuid4(), filename=parsed_body.filename)

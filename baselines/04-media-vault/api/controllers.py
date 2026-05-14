import uuid
from http import HTTPStatus

import msgspec

from dmr import Body, Controller, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer


class MediaUploadRequest(msgspec.Struct):
    filename: str
    size: int


class MediaUploadResponse(msgspec.Struct):
    uid: uuid.UUID
    filename: str


class MediaController(Controller[MsgspecSerializer]):
    responses = (
        ResponseSpec(return_type=MediaUploadResponse, status_code=HTTPStatus.CREATED),
    )

    @modify(status_code=HTTPStatus.CREATED)
    def post(self, parsed_body: Body[MediaUploadRequest]) -> MediaUploadResponse:
        return MediaUploadResponse(uid=uuid.uuid4(), filename=parsed_body.filename)

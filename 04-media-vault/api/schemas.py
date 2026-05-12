import uuid

import msgspec


class MediaCreate(msgspec.Struct):
    filename: str
    size: int


class MediaResponse(msgspec.Struct):
    uid: uuid.UUID
    filename: str

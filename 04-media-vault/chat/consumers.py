from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EchoConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        await self.accept()

    async def disconnect(self, code: int) -> None:
        pass

    async def receive_json(self, content: dict, **kwargs: object) -> None:
        await self.send_json(content)

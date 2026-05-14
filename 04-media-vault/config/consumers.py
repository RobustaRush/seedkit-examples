from channels.generic.websocket import AsyncJsonWebsocketConsumer


class EchoConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content: dict, **kwargs: object) -> None:
        await self.send_json(content)

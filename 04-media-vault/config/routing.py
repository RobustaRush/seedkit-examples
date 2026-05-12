from django.urls import path

from config.consumers import EchoConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),  # type: ignore[arg-type]
]

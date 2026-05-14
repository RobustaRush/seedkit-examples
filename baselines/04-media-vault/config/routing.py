from channels.routing import URLRouter
from django.urls import path

from jobs.consumers import EchoConsumer

websocket_urlpatterns = [
    path("ws/echo/", EchoConsumer.as_asgi()),
]

websocket_router = URLRouter(websocket_urlpatterns)

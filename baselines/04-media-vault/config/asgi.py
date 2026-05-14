import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_asgi_app = get_asgi_application()

from config.routing import websocket_router  # noqa: E402 — must come after get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(websocket_router)
        ),
    }
)

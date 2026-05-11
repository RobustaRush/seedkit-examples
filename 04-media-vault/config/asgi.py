import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

django_asgi_app = get_asgi_application()

from django.conf import settings  # noqa: E402 — after django.setup()

from config.routing import websocket_urlpatterns  # noqa: E402 — must import after django.setup()

_ws_app = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
# AllowedHostsOriginValidator rejects WS clients that omit the Origin header
# (e.g. Python test scripts). Browsers always send Origin, so the validator
# is meaningful only in production. Skip it in DEBUG so smoke tests work.
if not settings.DEBUG:
    _ws_app = AllowedHostsOriginValidator(_ws_app)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": _ws_app,
})

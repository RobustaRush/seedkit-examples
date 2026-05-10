from django.urls import path
from dmr.routing import Router

from .controllers import MediaController

router = Router(
    "api/",
    [
        path("media/", MediaController.as_view(), name="media"),
    ],
)

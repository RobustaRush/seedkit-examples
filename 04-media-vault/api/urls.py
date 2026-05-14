from django.urls import include, path
from dmr.routing import Router

from api.controllers import MediaController

router = Router(
    "media/",
    [
        path("", MediaController.as_view(), name="media-list"),
    ],
)

urlpatterns = [
    path(router.prefix, include((router.urls, "api"))),
]

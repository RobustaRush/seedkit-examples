from django.urls import path
from dmr.routing import Router

from api.controllers import MediaController

router = Router(
    "api/",
    [
        path("media/", MediaController.as_view(), name="media-upload"),
    ],
)

app_name = "api"
urlpatterns = router.urls

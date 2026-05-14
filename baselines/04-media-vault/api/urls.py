from django.urls import path

from dmr.routing import Router

from api.controllers import MediaController

app_name = "api"

router = Router(
    prefix="api/",
    urls=[
        path("media/", MediaController.as_view()),
    ],
)

urlpatterns = router.urls

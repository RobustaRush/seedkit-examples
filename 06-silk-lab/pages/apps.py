from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"

    def ready(self) -> None:
        from . import tasks  # noqa: F401

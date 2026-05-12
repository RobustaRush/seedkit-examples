from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = "jobs"

    def ready(self) -> None:
        from . import tasks  # noqa: F401  — register @task functions

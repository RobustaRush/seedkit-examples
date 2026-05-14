from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = "jobs"

    def ready(self):
        import jobs.tasks  # noqa: F401

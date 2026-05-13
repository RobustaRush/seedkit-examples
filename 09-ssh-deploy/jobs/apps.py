from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = "jobs"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import jobs.tasks  # noqa: F401 — registers tasks with the task registry

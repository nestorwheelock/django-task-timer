from django.apps import AppConfig


class TaskTimerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task_timer"

    def ready(self):
        """
        Import signals when the app is ready
        This ensures signals are registered
        """
        import task_timer.signals  # noqa

from django.apps import AppConfig

class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"

    def ready(self):
        # Import signals so receivers get registered
        from . import signals  # noqa: F401

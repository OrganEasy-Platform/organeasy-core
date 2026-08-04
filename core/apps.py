from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core"

    def ready(self) -> None:
        # Registra OpenApiAuthenticationExtension (SessionAuthentication401).
        import core.openapi  # noqa: F401

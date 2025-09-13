from django.apps import AppConfig


class SistemaApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sistema.api"
    label = "sistema_api"  # 👈 único

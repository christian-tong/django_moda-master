from django.apps import AppConfig


class EmpresaApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.empresa.api"
    label = "empresa_api"  # 👈 único

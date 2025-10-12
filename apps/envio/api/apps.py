# BCAKEND apps\envio\api\apps.py

from django.apps import AppConfig


class EnvioApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.envio.api"
    label = "envio_api"  # 👈 único

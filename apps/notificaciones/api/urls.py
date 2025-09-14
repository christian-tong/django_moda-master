# apps/notificaciones/api/urls.py
from django.urls import path
from .views import EnviarCorreoCumpleanosAPIView, RegistroCumpleanosListAPIView

app_name = "api-notificaciones"

urlpatterns = [
    path(
        "enviar-cumpleanos/",
        EnviarCorreoCumpleanosAPIView.as_view(),
        name="enviar-cumpleanos",
    ),
    path(
        "registros/",
        RegistroCumpleanosListAPIView.as_view(),
        name="registro-cumpleanos-list",
    ),
]

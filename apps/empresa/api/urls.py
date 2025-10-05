# BACKEND apps/empresa/api/urls.py

# apps/empresa/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConductorViewSet,
    AgenciaViewSet,
    RutaViewSet,
    VehiculoViewSet,
    AsientoViewSet,
)

app_name = "api-empresa"

# ⚠️ trailing_slash='/?' permite tanto con slash como sin slash
router = DefaultRouter(trailing_slash="/?")
router.register(r"conductores", ConductorViewSet, basename="conductor")
router.register(r"agencias", AgenciaViewSet, basename="agencia")
router.register(r"vehiculos", VehiculoViewSet, basename="vehiculo")
router.register(r"asientos", AsientoViewSet, basename="asiento")
router.register(r"rutas", RutaViewSet, basename="ruta")

urlpatterns = [
    path("", include(router.urls)),
]

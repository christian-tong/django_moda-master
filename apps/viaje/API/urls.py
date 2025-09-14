# apps/viaje/API/urls.py
"""
Rutas DRF para la app de viaje.
Exponen programaciones, asientos, embarques y manifiestos.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgramacionViajeViewSet,
    ProgramacionAsientoViewSet,
    EmbarqueViewSet,
    ManifiestoViewSet,
)

app_name = "api-viaje"

router = DefaultRouter(trailing_slash="/?")
router.register("programaciones", ProgramacionViajeViewSet, basename="programacion")
router.register("asientos", ProgramacionAsientoViewSet, basename="asiento")
router.register("embarques", EmbarqueViewSet, basename="embarque")
router.register("manifiestos", ManifiestoViewSet, basename="manifiesto")

urlpatterns = [
    path("", include(router.urls)),
]

# viaje/API/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ProgramacionViajeViewSet,
    ProgramacionAsientoViewSet,
    EmbarqueViewSet,
    ManifiestoViewSet,
    ReservarAsientoView,
)

app_name = "api"

router = DefaultRouter()
router.register(
    "programaciones", ProgramacionViajeViewSet, basename="programacionviaje"
)
router.register("asientos", ProgramacionAsientoViewSet, basename="programacionasiento")
router.register("embarques", EmbarqueViewSet, basename="embarque")
router.register("manifiestos", ManifiestoViewSet, basename="manifiesto")

urlpatterns = [
    # Rutas generales de la API
    path("reservar-asiento/", ReservarAsientoView.as_view(), name="reservar-asiento"),
]

# Agregamos las rutas del router
urlpatterns += router.urls

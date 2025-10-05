# BACKEND apps\facturacion\api\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FaturaBoletaViewSet

app_name = "api-facturacion"

router = DefaultRouter(trailing_slash="/?")
router.register(r"facturas", FaturaBoletaViewSet, basename="factura")

urlpatterns = [
    path("", include(router.urls)),
]

# BCAKEND apps\envio\api\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EncomiendaViewSet, LiquidacionViewSet

app_name = "api-envio"

router = DefaultRouter(trailing_slash="/?")
router.register(r"encomiendas", EncomiendaViewSet, basename="encomienda")
router.register(r"liquidaciones", LiquidacionViewSet, basename="liquidacion")

urlpatterns = [
    path("", include(router.urls)),
]

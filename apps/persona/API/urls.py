# persona/API/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PersonaJuridicaAPIView,
    PersonaNaturalAPIView,
    PersonaViewSet,
    PersonaListCreateAPIView,
    PersonaRetrieveUpdateDestroyAPIView,
)

app_name = "api"

router = DefaultRouter()
router.register(r"personas", PersonaViewSet)

urlpatterns = [
    # Rutas generales de la API
    path("persona-natural/", PersonaNaturalAPIView.as_view(), name="persona-natural"),
    path(
        "persona-juridica/", PersonaJuridicaAPIView.as_view(), name="persona-juridica"
    ),
    path("personas/", PersonaListCreateAPIView.as_view(), name="persona-list-create"),
    path(
        "personas/<int:pk>/",
        PersonaRetrieveUpdateDestroyAPIView.as_view(),
        name="persona-detail",
    ),
]

# Agregamos las rutas del router
urlpatterns += router.urls

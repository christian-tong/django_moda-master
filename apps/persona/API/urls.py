# BACKEND apps/persona/API/urls.py
"""
Rutas DRF para la app de persona.
Exponen CRUD de Persona, PersonaNatural y PersonaJuridica.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonaViewSet, PersonaNaturalViewSet, PersonaJuridicaViewSet

app_name = "api-persona"

router = DefaultRouter(trailing_slash="/?")
router.register(r"personas", PersonaViewSet, basename="persona")
router.register(
    r"personas-naturales", PersonaNaturalViewSet, basename="persona-natural"
)
router.register(
    r"personas-juridicas", PersonaJuridicaViewSet, basename="persona-juridica"
)

urlpatterns = [
    path("", include(router.urls)),
]

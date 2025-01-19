from django.urls import include, path
from django.contrib.auth.decorators import login_required
from .views import (
    PersonaJuridicaAPIView,
    PersonaNaturalAPIView,
    list,
    add,
    edit,
    autocomplite,
    buscarApiDoc,
    updateOrdenHappy,
    PersonaListCreateAPIView,
    PersonaRetrieveUpdateDestroyAPIView,
)
from rest_framework.routers import DefaultRouter
from .views import PersonaViewSet

app_name = "persona"

router = DefaultRouter()
router.register(r"personas", PersonaViewSet)


urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/persona-natural/", PersonaNaturalAPIView.as_view(), name="persona-natural"
    ),
    path(
        "api/persona-juridica/",
        PersonaJuridicaAPIView.as_view(),
        name="persona-juridica",
    ),
    path("list/", (list), name="list"),
    path("add/", login_required(add), name="add"),
    path("edit/<int:pk>", login_required(edit), name="edit"),
    path("autocomplite/", login_required(autocomplite), name="autocomplite"),
    path("buscar/api/doc", login_required(buscarApiDoc), name="buscar-api-doc"),
    path(
        "update/orden/happy",
        login_required(updateOrdenHappy),
        name="update-orden-happy",
    ),
    path(
        "api/personas/", PersonaListCreateAPIView.as_view(), name="persona-list-create"
    ),
    path(
        "api/personas/<int:pk>/",
        PersonaRetrieveUpdateDestroyAPIView.as_view(),
        name="persona-detail",
    ),
]

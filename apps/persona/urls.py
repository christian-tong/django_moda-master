# persona/urls.py
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from .views import list, add, edit, autocomplite, updateOrdenHappy

app_name = "persona"

urlpatterns = [
    # Incluye las URLs de API desde el archivo separado
    path("api/", include("apps.persona.API.urls", namespace="api")),
    # Rutas no relacionadas con la API
    path("list/", (list), name="list"),
    path("add/", login_required(add), name="add"),
    path("edit/<int:pk>", login_required(edit), name="edit"),
    path("autocomplite/", login_required(autocomplite), name="autocomplite"),
    path(
        "update/orden/happy",
        login_required(updateOrdenHappy),
        name="update-orden-happy",
    ),
]

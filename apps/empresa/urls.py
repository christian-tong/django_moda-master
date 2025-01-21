from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ConductorAdd,
    ConductorList,
    AgenciaAdd,
    AgenciaList,
    AgenciaUpdate,
    ConductorUpdate,
)

app_name = "empresa"
urlpatterns = [
    path("conductor/add", login_required(ConductorAdd.as_view()), name="conductor-add"),
    path(
        "conductor/list", login_required(ConductorList.as_view()), name="conductor-list"
    ),
    path(
        "conductor/update/<int:pk>",
        login_required(ConductorUpdate.as_view()),
        name="conductor-update",
    ),
    path("agencia/add", login_required(AgenciaAdd.as_view()), name="agencia-add"),
    path("agencia/list", login_required(AgenciaList.as_view()), name="agencia-list"),
    path(
        "agencia/update/<int:pk>",
        login_required(AgenciaUpdate.as_view()),
        name="agencia-update",
    ),
]

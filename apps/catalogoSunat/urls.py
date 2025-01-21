from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import importarUbigueo, autocomplite

app_name = "catalogosunat"
urlpatterns = [
    path("import/ubigueo", login_required(importarUbigueo), name="import-ubigueoo"),
    path("autocomplite/", autocomplite, name="autocomplite"),
]

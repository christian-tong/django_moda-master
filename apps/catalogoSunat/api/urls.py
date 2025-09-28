# BACKEND apps/catalogoSunat/api/urls.py

from django.urls import path
from .views import UbigeoListView

app_name = "api-catalogosunat"

urlpatterns = [
    path("ubigeos/", UbigeoListView.as_view(), name="api-ubigeo-list"),
]

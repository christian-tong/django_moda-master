# apps/sistema/api/urls.py

from django.urls import path
from .views import (
    UserListView,
    UserAddView,
    AccountLoginView,
    AccountLogoutView,
    MenuListView,
    UserAgenciaView,
    HomeIndexView,
)

app_name = "api-sistema"


urlpatterns = [
    # 📌 Usuarios
    path(
        "users/", UserListView.as_view(), name="api-user-list"
    ),  # GET → lista usuarios
    path(
        "users/add/", UserAddView.as_view(), name="api-user-add"
    ),  # POST → crear usuario
    # 📌 Autenticación
    path("auth/login/", AccountLoginView.as_view(), name="api-login"),  # POST → login
    path("auth/login", AccountLoginView.as_view()),  # Alias
    path(
        "auth/logout/", AccountLogoutView.as_view(), name="api-logout"
    ),  # POST → logout
    path(
        "auth/logout",
        AccountLogoutView.as_view(),
    ),  # Alias
    # 📌 Menús
    path(
        "menus/", MenuListView.as_view(), name="api-menu-list"
    ),  # GET → menús y submenús
    # 📌 Agencias
    path(
        "users/agencia/", UserAgenciaView.as_view(), name="api-user-agencia"
    ),  # POST → seleccionar agencia
    # 📌 Dashboard / Home
    path(
        "home/", HomeIndexView.as_view(), name="api-home-index"
    ),  # GET → datos dashboard
]

# apps/sistema/api/urls.py
from django.urls import path
from .views import (
    UserListView,
    UserAddView,
    UserDetailView,  # ✅ nueva vista para GET/PUT/DELETE
    AccountLoginView,
    AccountLogoutView,
    MenuListView,
    UserAgenciaView,
    HomeIndexView,
)

app_name = "api-sistema"

urlpatterns = [
    # 📌 Usuarios
    path("users/", UserListView.as_view(), name="api-user-list"),  # GET → lista
    path("users/add/", UserAddView.as_view(), name="api-user-add"),  # POST → crear
    path(
        "users/<int:pk>/", UserDetailView.as_view(), name="api-user-detail"
    ),  # ✅ detalle CRUD individual
    # 📌 Autenticación
    path("auth/login/", AccountLoginView.as_view(), name="api-login"),
    path("auth/login", AccountLoginView.as_view()),  # alias
    path("auth/logout/", AccountLogoutView.as_view(), name="api-logout"),
    path("auth/logout", AccountLogoutView.as_view()),  # alias
    # 📌 Menús
    path("menus/", MenuListView.as_view(), name="api-menu-list"),
    # 📌 Agencias
    path("users/agencia/", UserAgenciaView.as_view(), name="api-user-agencia"),
    # 📌 Dashboard / Home
    path("home/", HomeIndexView.as_view(), name="api-home-index"),
]

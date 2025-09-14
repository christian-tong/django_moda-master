# apps/sistema/api/views.py

import datetime
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from apps.caja.models import MovimientoCaja
from apps.persona.models import Persona
from apps.persona.views import listHappy
from apps.sistema.forms import UsuarioAgenciaForm, UsuarioForm, UsuarioLoginForm
from apps.sistema.models import Menu, Usuario


# ============================
# 📌 Usuarios
# ============================


class UserListView(APIView):
    """
    GET: Lista todos los usuarios registrados en el sistema.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = Usuario.objects.all().values()
        return Response({"entity": list(users)}, status=status.HTTP_200_OK)


class UserAddView(APIView):
    """
    POST: Crea un nuevo usuario con los datos enviados en el body.
    """

    def post(self, request):
        form = UsuarioForm(request.data)
        if form.is_valid():
            user = form.save(commit=False)
            user.date_joined = datetime.datetime.now()
            user.set_password(form.cleaned_data.get("password"))
            user.save()
            return Response(
                {"success": True, "id": user.id}, status=status.HTTP_201_CREATED
            )
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


# ============================
# 📌 Autenticación
# ============================


class AccountLoginView(APIView):
    """
    POST: Inicia sesión con usuario y contraseña.
    Devuelve info del usuario y la ruta de redirección.
    """

    permission_classes = [AllowAny]  # 👈 aquí lo hacemos público

    def post(self, request):
        form = UsuarioLoginForm(request.data)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user and user.is_active:
                login(request, user)
                agencias = Usuario.objects.get(id=request.user.id).agencia.all()

                # Serializamos al usuario
                from .serializers import UsuarioSerializer

                user_data = UsuarioSerializer(user).data

                if agencias:
                    if len(agencias) == 1:
                        request.session["agencia_id"] = agencias[0].id
                        request.session["agencia_nombre"] = agencias[0].nombre
                        request.session["agencia_uno"] = True
                        return Response(
                            {
                                "success": True,
                                "redirect": "/dashboard",  # 👈 Ahora usable en React
                                "user": user_data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "success": True,
                                "redirect": "/seleccionar-agencia",
                                "user": user_data,
                            },
                            status=status.HTTP_200_OK,
                        )
                else:
                    return Response(
                        {
                            "success": False,
                            "error": "Accedió con éxito, pero no tiene una agencia asignada.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {"success": False, "error": "Usuario o contraseña incorrectos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {"success": False, "errors": form.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AccountLogoutView(APIView):
    """
    POST: Cierra sesión y elimina la sesión activa.
    """

    def post(self, request):
        logout(request)
        request.session.flush()
        return Response({"success": True}, status=status.HTTP_200_OK)


# ============================
# 📌 Menús
# ============================


class MenuListView(APIView):
    """
    GET: Devuelve todos los menús y submenús en formato jerárquico.
    """

    def get(self, request):
        menus = Menu.objects.filter(padre=None).order_by("orden")
        items = {}

        for menu in menus:
            items[menu.nombre] = {
                "padre": list(Menu.objects.filter(id=menu.id).values()),
                "hijo": list(
                    Menu.objects.filter(padre=menu).order_by("orden").values()
                ),
            }

        return Response(items, status=status.HTTP_200_OK)


# ============================
# 📌 Selección de Agencia
# ============================


class UserAgenciaView(APIView):
    """
    POST: Selecciona la agencia activa del usuario y la guarda en sesión.
    """

    def post(self, request):
        form = UsuarioAgenciaForm(request.data, request=request)
        if form.is_valid():
            agencia = form.cleaned_data.get("agencia")
            request.session["agencia_id"] = agencia.id
            request.session["agencia_nombre"] = agencia.nombre
            return Response(
                {"redirect": "sistema:home-index"}, status=status.HTTP_200_OK
            )
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


# ============================
# 📌 Dashboard / Home
# ============================


class HomeIndexView(APIView):
    """
    GET: Devuelve datos del dashboard principal:
    - Total clientes
    - Total ingresos
    - Total egresos
    - Saldo
    - Lista de happy days (personas especiales del día)
    """

    def get(self, request):
        tclientes = Persona.objects.count()

        stingresos = MovimientoCaja.objects.filter(tipoMov__tipo="ingreso").aggregate(
            Sum("monto")
        )["monto__sum"]
        tingresos = stingresos if stingresos else 0

        stegresos = MovimientoCaja.objects.filter(tipoMov__tipo="egreso").aggregate(
            Sum("monto")
        )["monto__sum"]
        tegresos = stegresos if stegresos else 0

        saldo = tingresos - tegresos
        happyday = listHappy(request)

        data = {
            "tclientes": tclientes,
            "tingresos": tingresos,
            "tegresos": tegresos,
            "saldo": saldo,
            "entity": happyday["entity"],
            "paginator": happyday["paginator"],
            "add_ruta_get": happyday["add_ruta_get"],
            "q": happyday["q"],
        }
        return Response(data, status=status.HTTP_200_OK)


# ============================
# 📌 Errores personalizados
# ============================


def custom_permission_denied_view(request, exception):
    """
    Vista de error 403 personalizada.
    """
    return Response({"error": "Acceso denegado"}, status=status.HTTP_403_FORBIDDEN)

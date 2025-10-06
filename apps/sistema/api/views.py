# apps/sistema/api/views.py

# ================================================================
# 📁 Sistema API Views
# ------------------------------------------------
# Endpoints REST:
# - Listado, creación y detalle de usuarios
# - Autenticación (login / logout)
# - Listado jerárquico de menús
# - Selección de agencia
# - Datos del Dashboard (Home)
# ================================================================

from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from apps.caja.models import MovimientoCaja
from apps.persona.models import Persona, PersonaNatural
from apps.persona.views import listHappy
from apps.sistema.forms import UsuarioAgenciaForm, UsuarioLoginForm
from apps.sistema.models import Menu, Usuario
from .serializers import UsuarioSerializer


# ================================================================
# 📌 LISTAR USUARIOS
# ================================================================
class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = (
            Usuario.objects.all().select_related("persona").prefetch_related("agencia")
        )
        data = []

        for u in users:
            persona_nombre = None
            if u.persona_id:
                pn = PersonaNatural.objects.filter(persona=u.persona).first()
                if pn:
                    persona_nombre = (
                        f"{pn.nombres} {pn.apellidoP} {pn.apellidoM}".strip()
                    )
                else:
                    persona_nombre = u.persona.denominacion or "-"

            agencias = list(u.agencia.values_list("nombre", flat=True))

            data.append(
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "is_active": u.is_active,
                    "is_staff": u.is_staff,
                    "is_superuser": u.is_superuser,
                    "persona": persona_nombre,
                    "persona_id": u.persona_id,
                    "agencias": agencias,
                    "date_joined": u.date_joined,
                    "last_login": u.last_login,
                }
            )

        return Response({"entity": data}, status=status.HTTP_200_OK)


# ================================================================
# 📌 CREAR USUARIO
# ================================================================
class UserAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        username = data.get("username")
        email = data.get("email", "")
        password = data.get("password", "")
        persona_id = data.get("persona_id")
        agencia_ids = data.get("agencia_ids", [])
        is_active = data.get("is_active", True)

        if not username or not password:
            return Response(
                {"error": "username y password son obligatorios"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = Usuario(username=username, email=email, is_active=is_active)
        user.set_password(password)

        if persona_id:
            try:
                user.persona = Persona.objects.get(id=persona_id)
            except Persona.DoesNotExist:
                return Response({"error": "Persona no encontrada"}, status=400)

        user.save()

        # ✅ Asignar agencias si las hay
        if agencia_ids:
            user.agencia.set(agencia_ids)

        return Response(
            {"success": True, "id": user.id, "entity": UsuarioSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )

# ================================================================
# 📌 DETALLE / EDITAR / ELIMINAR USUARIO
# ================================================================
class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.is_active = data.get("is_active", user.is_active)

        if data.get("password"):
            user.set_password(data["password"])

        persona_id = data.get("persona_id")
        if persona_id:
            try:
                user.persona = Persona.objects.get(id=persona_id)
            except Persona.DoesNotExist:
                return Response({"error": "Persona no encontrada"}, status=400)

        # ✅ Asignar agencias (si llega)
        agencia_ids = data.get("agencia_ids")
        if isinstance(agencia_ids, list):
            user.agencia.set(agencia_ids)

        user.save()
        return Response(
            {"success": True, "entity": UsuarioSerializer(user).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================================================================
# 📌 LOGIN
# ================================================================
class AccountLoginView(APIView):
    """POST: Inicia sesión con usuario y contraseña."""

    permission_classes = [AllowAny]

    def post(self, request):
        form = UsuarioLoginForm(request.data)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user and user.is_active:
                login(request, user)
                agencias = Usuario.objects.get(id=request.user.id).agencia.all()
                user_data = UsuarioSerializer(user).data

                if agencias.exists():
                    if agencias.count() == 1:
                        agencia = agencias.first()
                        request.session["agencia_id"] = agencia.id
                        request.session["agencia_nombre"] = agencia.nombre
                        request.session["agencia_uno"] = True
                        return Response(
                            {
                                "success": True,
                                "redirect": "/dashboard",
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

                # 🚫 Sin agencias
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


# ================================================================
# 📌 LOGOUT
# ================================================================
class AccountLogoutView(APIView):
    """POST: Cierra sesión y elimina la sesión activa."""

    def post(self, request):
        logout(request)
        request.session.flush()
        return Response({"success": True}, status=status.HTTP_200_OK)


# ================================================================
# 📌 MENÚS
# ================================================================
class MenuListView(APIView):
    """GET: Devuelve todos los menús y submenús en formato jerárquico."""

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


# ================================================================
# 📌 SELECCIÓN DE AGENCIA
# ================================================================
class UserAgenciaView(APIView):
    """POST: Selecciona la agencia activa del usuario y la guarda en sesión."""

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


# ================================================================
# 📌 DASHBOARD / HOME
# ================================================================
class HomeIndexView(APIView):
    """GET: Devuelve métricas y cumpleaños del día para el Dashboard."""

    def get(self, request):
        tclientes = Persona.objects.count()
        stingresos = (
            MovimientoCaja.objects.filter(tipoMov__tipo="ingreso").aggregate(
                Sum("monto")
            )["monto__sum"]
            or 0
        )
        stegresos = (
            MovimientoCaja.objects.filter(tipoMov__tipo="egreso").aggregate(
                Sum("monto")
            )["monto__sum"]
            or 0
        )
        saldo = stingresos - stegresos
        happyday = listHappy(request)

        data = {
            "tclientes": tclientes,
            "tingresos": stingresos,
            "tegresos": stegresos,
            "saldo": saldo,
            "entity": happyday["entity"],
            "paginator": happyday["paginator"],
            "add_ruta_get": happyday["add_ruta_get"],
            "q": happyday["q"],
        }

        return Response(data, status=status.HTTP_200_OK)


# ================================================================
# 📌 ERRORES PERSONALIZADOS
# ================================================================
def custom_permission_denied_view(request, exception):
    """Vista personalizada de error 403 (acceso denegado)."""
    return Response({"error": "Acceso denegado"}, status=status.HTTP_403_FORBIDDEN)

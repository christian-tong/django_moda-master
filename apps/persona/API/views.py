# BACKEND apps/persona/API/views.py

"""
ViewSets DRF para la app de persona.
Compatibles con el frontend actual, extendidos con:
- búsqueda en APIs externas (RUC/DNI)
- endpoint de cumpleaños por mes
- CRUD de PersonaNatural y PersonaJuridica
"""

from datetime import date
import requests
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Persona, PersonaNatural, PersonaJuridica
from .serializers import (
    PersonaListSerializer,
    PersonaDetailSerializer,
    PersonaWriteSerializer,
    PersonaNaturalSerializer,
    PersonaNaturalWriteSerializer,
    PersonaJuridicaSerializer,
    PersonaJuridicaWriteSerializer,
)
from apps.empresa.api.views import StandardResultsSetPagination, ok, fail


# -----------------------------
# Persona
# -----------------------------
class PersonaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Personas con filtros y búsquedas adicionales.
    - list: búsqueda por denominación o numDoc (?q=...)
    - autocomplete: búsqueda rápida (?term=...)
    - buscar-por-dni: endpoint rápido para validar DNI
    - buscar-api-doc: consulta en servicios externos (RENIEC / SUNAT)
    - cumpleanos-por-mes: obtiene cumpleaños de personas naturales en un mes
    """

    queryset = Persona.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return PersonaListSerializer
        elif self.action == "retrieve":
            return PersonaDetailSerializer
        return PersonaWriteSerializer

    def list(self, request, *args, **kwargs):
        """
        Listado de personas.
        - Si ?q=... → busca por denominación o numDoc y devuelve TODOS los resultados (sin paginación).
        - Si no hay q → devuelve paginado normal.
        """
        qs = self.get_queryset()
        q = request.GET.get("q")

        if q:
            # Filtro estilo SQL LIKE en denominación o numDoc
            qs = qs.filter(
                Q(denominacion__icontains=q) | Q(numDoc__icontains=q)
            ).distinct()

            # 🚨 No usamos paginate_queryset, devolvemos todo
            serializer = self.get_serializer(qs, many=True)
            return Response(
                {"count": len(serializer.data), "results": {"entity": serializer.data}}
            )

        # Caso sin búsqueda → paginado normal
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    @action(detail=False, methods=["get"], url_path="autocomplete")
    def autocomplete(self, request):
        """
        Autocomplete para selects (mínimo 2 caracteres).
        Busca por denominación o número de documento.
        Ejemplo: /persona/api/personas/autocomplete/?term=carbajal
        """
        term = request.GET.get("term")
        filtro = request.GET.get("filtro")
        if not term or len(term) < 2:
            return fail(message="El parámetro 'term' es requerido (mín. 2 caracteres).")

        query = Q(denominacion__icontains=term) | Q(numDoc__icontains=term)
        if filtro == "personal":
            query &= Q(ispersonal=True)

        personas = Persona.objects.filter(query).distinct()[:10]
        serializer = PersonaListSerializer(personas, many=True)
        return ok(serializer.data)

    @action(detail=False, methods=["get"], url_path="buscar-por-dni")
    def buscar_por_dni(self, request):
        """
        Consulta por DNI en la base local.
        Ejemplo: /persona/api/personas/buscar-por-dni/?dni=12345678
        """
        dni = request.GET.get("dni")
        if not dni:
            return fail(message="El parámetro 'dni' es requerido.")

        try:
            persona = Persona.objects.get(numDoc=dni)
            return ok(PersonaDetailSerializer(persona).data)
        except Persona.DoesNotExist:
            return fail(
                message="No se encontró ninguna persona con ese DNI.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["post"], url_path="buscar-api-doc")
    def buscar_api_doc(self, request):
        """
        Consulta datos en APIs externas (RENIEC / SUNAT).
        Recibe JSON:
        {
            "tipodoc": "DNI" o "RUC",
            "numdoc": "XXXXXXXX"
        }
        """
        datos = request.data
        tipodoc = datos.get("tipodoc")
        numdoc = datos.get("numdoc")

        if not tipodoc or not numdoc:
            return fail(message="Parámetros 'tipodoc' y 'numdoc' son requeridos.")

        try:
            if tipodoc == "DNI":
                url_dni = f"https://consulta.api-peru.com/api/dni/{numdoc}"
                response = requests.get(url_dni).json()
                if not response.get("success"):
                    return fail(message="No se encontró información del DNI en la API.")
                data = {
                    "denominacion": response["data"]["nombre_completo"],
                    "nombres": response["data"]["nombres"],
                    "apellido_paterno": response["data"]["apellido_paterno"],
                    "apellido_materno": response["data"]["apellido_materno"],
                    "sexo": "M" if response["data"]["sexo"] == "MASCULINO" else "F",
                    "fecha_nacimiento": response["data"]["fecha_nacimiento"],
                }
                return ok(data)

            elif tipodoc == "RUC":
                url_ruc = f"https://api.apis.net.pe/v1/ruc?numero={numdoc}"
                response = requests.get(url_ruc).json()
                data = {
                    "denominacion": response.get("nombre"),
                    "direccion": response.get("direccion"),
                    "ubigeo": response.get("ubigeo"),
                    "distrito": response.get("distrito"),
                    "provincia": response.get("provincia"),
                    "departamento": response.get("departamento"),
                }
                return ok(data)

            return fail(message="El tipo de documento no es válido (DNI o RUC).")

        except Exception as e:
            return fail(message=f"Error consultando API externa: {str(e)}")

    @action(detail=False, methods=["get"], url_path="cumpleanos-por-mes")
    def cumpleanos_por_mes(self, request):
        """
        Devuelve lista de cumpleaños por mes.
        Query param requerido: ?mes=1..12
        Ejemplo: /persona/api/personas/cumpleanos-por-mes/?mes=3
        """
        try:
            mes = int(request.GET.get("mes"))
        except (TypeError, ValueError):
            return fail(
                message="El parámetro 'mes' es requerido y debe ser un número (1-12)."
            )

        personas = PersonaNatural.objects.filter(fechaNac__month=mes).select_related(
            "persona"
        )

        data = []
        for p in personas:
            if not p.fechaNac:
                continue
            edad = date.today().year - p.fechaNac.year
            data.append(
                {
                    "id": p.id,
                    "nombre_completo": f"{p.nombres} {p.apellidoP} {p.apellidoM}",
                    "fecha_nacimiento": p.fechaNac.isoformat(),
                    "dia": p.fechaNac.day,
                    "mes": p.fechaNac.month,
                    "edad": edad,
                    "celular": p.persona.movilUno or p.persona.movilDos,
                }
            )

        return ok(data)


# -----------------------------
# PersonaNatural
# -----------------------------
class PersonaNaturalViewSet(viewsets.ModelViewSet):
    """
    CRUD de Personas Naturales.
    """

    queryset = PersonaNatural.objects.all().select_related("persona")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PersonaNaturalSerializer
        return PersonaNaturalWriteSerializer


# -----------------------------
# PersonaJuridica
# -----------------------------
class PersonaJuridicaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Personas Jurídicas.
    """

    queryset = PersonaJuridica.objects.all().select_related("persona")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PersonaJuridicaSerializer
        return PersonaJuridicaWriteSerializer

# region Imports
from django.db.models import Q
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.urls import reverse_lazy

from apps.empresa.models import Conductor, Agencia
from .serializers import (
    ConductorListSerializer,
    ConductorDetailSerializer,
    ConductorWriteSerializer,
    AgenciaListSerializer,
    AgenciaDetailSerializer,
    AgenciaWriteSerializer,
)

# endregion


# region Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 200


# endregion


# region Helper responses
def ok(entity=None, message=None, status_code=status.HTTP_200_OK):
    """
    /// <summary>
    /// Respuesta uniforme que mantiene la clave 'entity' como en las vistas originales.
    /// </summary>
    """
    return Response(
        {"ok": True, "entity": entity, "message": message, "errors": None},
        status=status_code,
    )


def fail(errors=None, message=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {"ok": False, "entity": None, "message": message, "errors": errors},
        status=status_code,
    )


# endregion


# region Conductor ViewSet
class ConductorViewSet(viewsets.ModelViewSet):
    """
    /// <summary>
    /// CRUD de Conductor con filtros por q (denominación o numDoc).
    /// GET -> listado paginado con 'entity'
    /// POST -> creación
    /// PUT/PATCH -> actualización
    /// </summary>
    """

    queryset = Conductor.objects.all().select_related("chofer")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list"]:
            return ConductorListSerializer
        elif self.action in ["retrieve"]:
            return ConductorDetailSerializer
        return ConductorWriteSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(chofer__denominacion__icontains=q) | Q(chofer__numDoc__icontains=q)
            ).distinct()
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = ConductorWriteSerializer(data=request.data)
        if serializer.is_valid():
            conductor = serializer.save()
            out_ser = ConductorDetailSerializer(conductor)
            return ok(
                {
                    "object": out_ser.data,
                    "success_url": reverse_lazy("empresa:conductor-list"),
                },
                status_code=status.HTTP_201_CREATED,
            )
        return fail(errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ConductorWriteSerializer(
            instance, data=request.data, partial=False
        )
        if serializer.is_valid():
            conductor = serializer.save()
            out_ser = ConductorDetailSerializer(conductor)
            return ok(
                {
                    "object": out_ser.data,
                    "success_url": reverse_lazy("empresa:conductor-list"),
                }
            )
        return fail(errors=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ConductorWriteSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            conductor = serializer.save()
            out_ser = ConductorDetailSerializer(conductor)
            return ok(
                {
                    "object": out_ser.data,
                    "success_url": reverse_lazy("empresa:conductor-list"),
                }
            )
        return fail(errors=serializer.errors)


# endregion


# region Agencia ViewSet
class AgenciaViewSet(viewsets.ModelViewSet):
    """
    /// <summary>
    /// CRUD de Agencia con filtros por nombre exacto.
    /// </summary>
    """

    queryset = Agencia.objects.all().select_related("ubigeo", "responsable", "empresa")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list"]:
            return AgenciaListSerializer
        elif self.action in ["retrieve"]:
            return AgenciaDetailSerializer
        return AgenciaWriteSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.GET.get("q")
        if q:
            qs = qs.filter(nombre=q).distinct()
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = AgenciaWriteSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            empresa_principal = Agencia.objects.filter(tipo="PRINCIPAL").first()
            empresa_persona = empresa_principal.empresa if empresa_principal else None

            agencia_obj = Agencia.objects.create(
                nombre=data.get("nombre"),
                ubigeo=data.get("ubigeo"),
                responsable=data.get("responsable"),
                direccion=data.get("direccion"),
                fijo=data.get("fijo"),
                movilUno=data.get("movilUno"),
                movilDos=data.get("movilDos"),
                correo=data.get("correo"),
                foto=data.get("foto", None),
                activo=data.get("activo", True),
                codigoSerieDocumento=data.get("codigoSerieDocumento", None),
                isruta=data.get("isruta", False),
                empresa=empresa_persona,
                tipo="SUCURSAL",
            )
            out_ser = AgenciaDetailSerializer(agencia_obj)
            return ok(
                {
                    "object": out_ser.data,
                    "success_url": reverse_lazy("empresa:agencia-list"),
                },
                status_code=status.HTTP_201_CREATED,
            )
        return fail(errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AgenciaWriteSerializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            for k, v in serializer.validated_data.items():
                setattr(instance, k, v)
            instance.save()
            out_ser = AgenciaDetailSerializer(instance)
            return ok(
                {
                    "object": out_ser.data,
                    "success_url": reverse_lazy("empresa:agencia-list"),
                }
            )
        return fail(errors=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AgenciaWriteSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            for k, v in serializer.validated_data.items():
                setattr(instance, k, v)
            instance.save()
            out_ser = AgenciaDetailSerializer(instance)
            return ok(
                {
                    "object": out_ser.data,
                    "success_url": reverse_lazy("empresa:agencia-list"),
                }
            )
        return fail(errors=serializer.errors)


# endregion

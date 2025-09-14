# apps/viaje/API/views.py
"""
ViewSets DRF para la app de viaje.
Migran la lógica de las vistas Django clásicas a APIs RESTful.
Incluyen helpers ok()/fail() para respuestas uniformes.
"""

from datetime import datetime
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import ProgramacionViaje, ProgramacionAsiento, Embarque, Manifiesto
from .serializers import (
    ProgramacionViajeListSerializer,
    ProgramacionViajeDetailSerializer,
    ProgramacionViajeWriteSerializer,
    ProgramacionAsientoSerializer,
    ProgramacionAsientoWriteSerializer,
    EmbarqueListSerializer,
    EmbarqueDetailSerializer,
    EmbarqueWriteSerializer,
    ManifiestoListSerializer,
    ManifiestoDetailSerializer,
    ManifiestoWriteSerializer,
)

# Helpers reutilizados de empresa
from apps.empresa.api.views import StandardResultsSetPagination, ok, fail


# -----------------------------
# ProgramacionViaje
# -----------------------------
class ProgramacionViajeViewSet(viewsets.ModelViewSet):
    """
    CRUD de Programación de Viajes.
    - Al crear: se generan automáticamente asientos y manifiesto.
    """

    queryset = ProgramacionViaje.objects.all().select_related(
        "vehiculo", "rutaOrigen", "rutaDestino"
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ProgramacionViajeListSerializer
        elif self.action == "retrieve":
            return ProgramacionViajeDetailSerializer
        return ProgramacionViajeWriteSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        fecha = request.GET.get("fecha")
        origen = request.GET.get("origen")
        destino = request.GET.get("destino")

        if fecha:
            try:
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                qs = qs.filter(fechaViaje=fecha)
            except ValueError:
                return fail(message="Formato de fecha inválido, use AAAA-MM-DD")

        if origen:
            qs = qs.filter(rutaOrigen_id=origen)
        if destino:
            qs = qs.filter(rutaDestino_id=destino)

        page = self.paginate_queryset(qs.order_by("-fechaViaje"))
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = ProgramacionViajeWriteSerializer(data=request.data)
        if serializer.is_valid():
            prog = serializer.save()
            # 🔥 lógica extra: crear asientos para el vehículo
            for asiento in prog.vehiculo.asiento_set.all():
                ProgramacionAsiento.objects.create(
                    programacionViaje=prog,
                    asiento=asiento,
                    estado=asiento.estado,
                    precio=prog.precio,
                )
            # 🔥 lógica extra: crear manifiesto vacío
            Manifiesto.objects.create(
                numDocumento=f"MA{prog.id:05d}",
                programacionViaje=prog,
                vehiculo=prog.vehiculo,
                piloto=prog.piloto,
                copiloto=prog.copiloto,
                fechaViaje=prog.fechaViaje,
            )
            return ok(
                ProgramacionViajeDetailSerializer(prog).data, status.HTTP_201_CREATED
            )
        return fail(errors=serializer.errors)


# -----------------------------
# ProgramacionAsiento
# -----------------------------
class ProgramacionAsientoViewSet(viewsets.ModelViewSet):
    queryset = ProgramacionAsiento.objects.all().select_related(
        "programacionViaje", "asiento"
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProgramacionAsientoSerializer
        return ProgramacionAsientoWriteSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        prog_id = request.GET.get("programacion_id")
        if prog_id:
            qs = qs.filter(programacionViaje_id=prog_id)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    @action(detail=True, methods=["get"], url_path="matriz")
    def matriz(self, request, pk=None):
        """
        Devuelve los asientos en formato de matriz (filas x columnas).
        """
        programacion = self.get_object()
        asientos = ProgramacionAsiento.objects.filter(
            programacionViaje=programacion
        ).order_by("asiento__codigoMatrix")

        filas = {}
        for a in asientos:
            fila = a.asiento.codigoMatrix // 10
            col = a.asiento.codigoMatrix % 10
            filas.setdefault(fila, []).append(
                {
                    "id": a.id,
                    "numero": a.asiento.numero,
                    "estado": a.estado,
                    "precio": a.precio,
                    "columna": col,
                }
            )

        matriz = [
            sorted(filas[f], key=lambda x: x["columna"]) for f in sorted(filas.keys())
        ]
        return ok({"programacion": programacion.id, "matriz": matriz})


# -----------------------------
# Embarque
# -----------------------------
class EmbarqueViewSet(viewsets.ModelViewSet):
    queryset = Embarque.objects.all().select_related("programacionViaje", "pasajero")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return EmbarqueListSerializer
        elif self.action == "retrieve":
            return EmbarqueDetailSerializer
        return EmbarqueWriteSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(pasajero__denominacion__icontains=q)
                | Q(pasajero__numDoc__icontains=q)
            )
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})


# -----------------------------
# Manifiesto
# -----------------------------
class ManifiestoViewSet(viewsets.ModelViewSet):
    queryset = Manifiesto.objects.all().select_related("programacionViaje", "vehiculo")
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ManifiestoListSerializer
        elif self.action == "retrieve":
            return ManifiestoDetailSerializer
        return ManifiestoWriteSerializer

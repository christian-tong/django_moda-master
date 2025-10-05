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

from desatendidos.correlativoDoc import incrementa

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
from django.db import transaction


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
# apps/viaje/API/views.py


class EmbarqueViewSet(viewsets.ModelViewSet):
    queryset = Embarque.objects.all().select_related(
        "programacionViaje", "pasajero", "lugar_abordo", "lugar_bajada"
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return EmbarqueListSerializer
        elif self.action == "retrieve":
            return EmbarqueDetailSerializer
        return EmbarqueWriteSerializer

    # ------- LIST -------
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        q = request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(pasajero__denominacion__icontains=q)
                | Q(pasajero__numDoc__icontains=q)
                | Q(numDocumento__icontains=q)
            )
        page = self.paginate_queryset(qs.order_by("-create"))
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    # ------- CREATE (numDocumento auto + asiento -> vendido) -------
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Generar correlativo si no viene
        if not data.get("numDocumento"):
            try:
                data["numDocumento"] = incrementa(request, "PA")["correlativo"]
            except Exception as e:
                return fail(message=f"No se pudo generar correlativo: {e}")

        # Validar y bloquear que venga idasiento coherente (opcional si el flujo no lo usa)
        idasiento = data.get("idasiento")
        prog_id = data.get("programacionViaje")
        num_asiento = data.get("numAsiento")

        if not (idasiento and prog_id and num_asiento):
            # Permitimos crear sin asiento solo si así lo usas; si no, obliga:
            # return fail(message="Debe enviar programacionViaje, idasiento y numAsiento")
            pass

        serializer = EmbarqueWriteSerializer(data=data)
        if not serializer.is_valid():
            return fail(errors=serializer.errors)

        embarque = serializer.save()

        # Si vino asiento, marcarlo como vendido asegurando coherencia
        if idasiento and prog_id and num_asiento:
            try:
                asiento = ProgramacionAsiento.objects.select_for_update().get(
                    pk=idasiento, programacionViaje_id=prog_id
                )
            except ProgramacionAsiento.DoesNotExist:
                transaction.set_rollback(True)
                return fail(message="Asiento inválido para la programación enviada.")

            if asiento.estado != "libre":
                transaction.set_rollback(True)
                return fail(message="El asiento ya no está disponible.")

            asiento.estado = "vendido"
            # Mantener precio de asiento si no se mandó precio en body
            if not data.get("precio"):
                embarque.precio = asiento.precio or 0
                embarque.save(update_fields=["precio"])
            asiento.save()

        return ok(
            EmbarqueDetailSerializer(embarque).data, status_code=status.HTTP_201_CREATED
        )

    # ------- UPDATE (numDocumento inmutable + manejo de cambio de asiento opcional) -------
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance: Embarque = self.get_object()
        data = request.data.copy()

        # Blindar numDocumento
        if "numDocumento" in data and data["numDocumento"] != (
            instance.numDocumento or ""
        ):
            return fail(message="No se permite modificar numDocumento.")

        # Detectar cambio de asiento (misma programación)
        new_num_asiento = data.get("numAsiento")
        idasiento = data.get("idasiento")
        same_programacion = str(
            data.get("programacionViaje") or instance.programacionViaje_id
        ) == str(instance.programacionViaje_id)

        # Gestionar cambio de asiento si aplica
        if (
            new_num_asiento
            and idasiento
            and same_programacion
            and new_num_asiento != instance.numAsiento
        ):
            # Liberar asiento anterior
            ProgramacionAsiento.objects.filter(
                programacionViaje_id=instance.programacionViaje_id,
                asiento__numero=instance.numAsiento,
            ).update(estado="libre")

            # Ocupar nuevo
            try:
                asiento_nuevo = ProgramacionAsiento.objects.select_for_update().get(
                    pk=idasiento, programacionViaje_id=instance.programacionViaje_id
                )
            except ProgramacionAsiento.DoesNotExist:
                transaction.set_rollback(True)
                return fail(message="Asiento destino inválido.")

            if asiento_nuevo.estado != "libre":
                transaction.set_rollback(True)
                return fail(message="El asiento destino no está disponible.")
            asiento_nuevo.estado = "vendido"
            asiento_nuevo.save()

        serializer = EmbarqueWriteSerializer(instance, data=data, partial=False)
        if serializer.is_valid():
            embarque = serializer.save()
            return ok(EmbarqueDetailSerializer(embarque).data)
        return fail(errors=serializer.errors)

    # ------- PARTIAL UPDATE (mismas reglas) -------
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance: Embarque = self.get_object()
        data = request.data.copy()

        if "numDocumento" in data and data["numDocumento"] != (
            instance.numDocumento or ""
        ):
            return fail(message="No se permite modificar numDocumento.")

        # Check-in simple por PATCH (opcional)
        if "enSala" in data:
            instance.enSala = bool(data["enSala"])
            instance.save(update_fields=["enSala"])

        serializer = EmbarqueWriteSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            embarque = serializer.save()
            return ok(EmbarqueDetailSerializer(embarque).data)
        return fail(errors=serializer.errors)

    # ------- DELETE (libera asiento) -------
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance: Embarque = self.get_object()

        # Liberar asiento si existe
        if instance.programacionViaje_id and instance.numAsiento:
            ProgramacionAsiento.objects.filter(
                programacionViaje_id=instance.programacionViaje_id,
                asiento__numero=instance.numAsiento,
            ).update(estado="libre")

        instance.delete()
        return ok(message="Embarque eliminado.")

    # ------- ACCIÓN: Check-in -------
    @action(detail=True, methods=["post"], url_path="checkin")
    def checkin(self, request, pk=None):
        """
        Marca/desmarca enSala. Si envías {"enSala": true|false} lo respeta;
        si no envías nada, marca True por defecto.
        """
        embarque = self.get_object()
        en_sala = request.data.get("enSala", True)
        embarque.enSala = bool(en_sala)
        embarque.save(update_fields=["enSala"])
        return ok(EmbarqueDetailSerializer(embarque).data, "Check-in actualizado")

    # ------- ACCIÓN: Reprogramar -------
    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="reprogramar")
    def reprogramar(self, request, pk=None):
        """
        Reprograma el embarque a otra Programación/Asiento.
        Espera: programacionViaje, idasiento, numAsiento.
        """
        embarque = self.get_object()
        prog_id = request.data.get("programacionViaje")
        asiento_id = request.data.get("idasiento")
        num_asiento = request.data.get("numAsiento")

        if not (prog_id and asiento_id and num_asiento):
            return fail(message="Debe enviar programacionViaje, idasiento y numAsiento")

        try:
            prog = ProgramacionViaje.objects.get(pk=prog_id)
            asiento_nuevo = ProgramacionAsiento.objects.select_for_update().get(
                pk=asiento_id, programacionViaje=prog
            )
        except (ProgramacionViaje.DoesNotExist, ProgramacionAsiento.DoesNotExist):
            transaction.set_rollback(True)
            return fail(message="Programación o asiento inválido")

        if asiento_nuevo.estado != "libre":
            transaction.set_rollback(True)
            return fail(message="El asiento destino no está disponible")

        # Liberar asiento anterior
        if embarque.programacionViaje_id and embarque.numAsiento:
            ProgramacionAsiento.objects.filter(
                programacionViaje=embarque.programacionViaje,
                asiento__numero=embarque.numAsiento,
            ).update(estado="libre")

        # Asignar nuevo
        asiento_nuevo.estado = "vendido"
        asiento_nuevo.save()

        embarque.programacionViaje = prog
        embarque.numAsiento = num_asiento
        embarque.escambio = True
        if hasattr(request.user, "persona"):
            embarque.usuario = request.user.persona
        # Precio por defecto del nuevo asiento si no se envía precio
        if not request.data.get("precio"):
            embarque.precio = asiento_nuevo.precio or embarque.precio
        embarque.save()

        return ok(EmbarqueDetailSerializer(embarque).data, "Reprogramación exitosa")

    # ------- ACCIÓN: Print data (para React-PDF) -------
    @action(detail=True, methods=["get"], url_path="print-data")
    def print_data(self, request, pk=None):
        """
        Devuelve la estructura de datos lista para que el frontend (React-PDF)
        genere el PDF del boleto. No genera PDF en backend.
        """
        e: Embarque = self.get_object()
        p = e.pasajero
        prog = e.programacionViaje
        veh = prog.vehiculo if prog else None

        data = {
            "numDocumento": e.numDocumento,
            "fechaEmision": e.create,
            "pasajero": {
                "id": p.id,
                "denominacion": getattr(p, "denominacion", None),
                "numDoc": getattr(p, "numDoc", None),
            },
            "programacion": (
                {
                    "id": prog.id if prog else None,
                    "nombreViaje": getattr(prog, "nombreViaje", None),
                    "fechaViaje": getattr(prog, "fechaViaje", None),
                    "horaViaje": getattr(prog, "horaViaje", None),
                    "rutaOrigen": (
                        getattr(prog.rutaOrigen, "nombre", None) if prog else None
                    ),
                    "rutaDestino": (
                        getattr(prog.rutaDestino, "nombre", None) if prog else None
                    ),
                }
                if prog
                else None
            ),
            "vehiculo": (
                {
                    "id": veh.id if veh else None,
                    "placa": getattr(veh, "placa", None),
                    "modelo": getattr(veh, "modelo", None),
                    "numPlazas": getattr(veh, "numPlazas", None),
                }
                if veh
                else None
            ),
            "embarque": {
                "lugar_abordo": getattr(e.lugar_abordo, "nombre", None),
                "lugar_bajada": getattr(e.lugar_bajada, "nombre", None),
                "hora_abordo": e.hora_abordo,
                "numAsiento": e.numAsiento,
                "precio": e.precio,
                "observacion": e.observacion,
                "telefono": e.telefono,
            },
            # Extra opcional: podrías generar un texto QR/payload de validación
            "qrPayload": f"EMB-{e.id}-{e.numDocumento or 'NA'}",
        }
        return ok(data)


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

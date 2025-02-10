from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets

from ..models import (
    Embarque,
    Manifiesto,
    ProgramacionAsiento,
    ProgramacionViaje,
)

from rest_framework.viewsets import ViewSet
from .serializers import (
    AsientosDisponiblesSerializer,
    ProgramacionViajeSerializer,
    EmbarqueSerializer,
    ManifiestoSerializer,
    ReservarAsientoSerializer,
)
from apps.persona.models import Persona

from rest_framework.exceptions import ValidationError

from rest_framework.views import APIView


class ProgramacionViajeViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramacionViajeSerializer

    def get_queryset(self):
        """
        Filtra las programaciones de viaje por fecha o por id pasado como parámetro.
        Si no se pasa ningún parámetro, devuelve todas las programaciones.
        """
        queryset = ProgramacionViaje.objects.all()
        fecha_param = self.request.query_params.get("fecha", None)
        id_param = self.request.query_params.get("id", None)

        if id_param:
            try:
                # Filtrar por id
                return queryset.filter(id=id_param)
            except ValueError:
                raise ValidationError({"id": "El id debe ser un número válido."})

        if fecha_param:
            try:
                # Intentar convertir el parámetro a un objeto de tipo date
                fecha = datetime.strptime(fecha_param, "%Y-%m-%d").date()
                # Filtrar por fecha exacta
                return queryset.filter(fechaViaje=fecha)
            except ValueError:
                raise ValidationError(
                    {"fecha": "El formato de la fecha debe ser AAAA-MM-DD."}
                )

        # Si no se pasa ningún parámetro, devolver todas las programaciones
        return queryset


class ProgramacionAsientoViewSet(ViewSet):
    @action(detail=True, methods=["get"], url_path="asientos_disponibles")
    def asientos_disponibles(self, request, pk=None):
        # Obtener la programación del viaje
        try:
            programacion_viaje = ProgramacionViaje.objects.get(pk=pk)
        except ProgramacionViaje.DoesNotExist:
            return Response(
                {"error": "Programación de viaje no encontrada"}, status=404
            )

        # Filtrar asientos según el estado
        libres = ProgramacionAsiento.objects.filter(
            programacionViaje=programacion_viaje, estado="libre"
        )
        vendidos = ProgramacionAsiento.objects.filter(
            programacionViaje=programacion_viaje, estado="vendido"
        )

        # Serializar los datos
        serializer = AsientosDisponiblesSerializer(
            {"libres": libres, "vendidos": vendidos}
        )

        return Response(serializer.data, status=200)

    @action(detail=False, methods=["post"], url_path="vender_asientos")
    def vender_asientos(self, request):
        # Validar los datos de entrada
        serializer = ReservarAsientoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extraer los datos validados
        programacion_viaje_id = serializer.validated_data["programacion_viaje_id"]
        asientos_ids = serializer.validated_data["asientos_ids"]
        nro_documento = serializer.validated_data["nro_documento"]

        # Verificar que la programación del viaje existe
        try:
            programacion_viaje = ProgramacionViaje.objects.get(pk=programacion_viaje_id)
        except ProgramacionViaje.DoesNotExist:
            return Response(
                {"error": "Programación de viaje no encontrada"}, status=404
            )

        # Buscar al cliente por número de documento
        try:
            cliente = Persona.objects.get(numDoc=nro_documento)
        except Persona.DoesNotExist:
            return Response(
                {
                    "error": "Cliente no encontrado con el número de documento proporcionado."
                },
                status=404,
            )

        # Inicializar las listas para asientos actualizados y errores
        asientos_actualizados = []
        errores_asientos = []

        # Procesar cada asiento solicitado
        for asiento_id in asientos_ids:
            try:
                asiento = ProgramacionAsiento.objects.get(
                    id=asiento_id, programacionViaje=programacion_viaje, estado="libre"
                )
                # Cambiar el estado del asiento a "vendido"
                asiento.estado = "vendido"
                asiento.save()

                # Crear el registro en la tabla Embarque con el número de asiento
                Embarque.objects.create(
                    programacionViaje=programacion_viaje,
                    pasajero=cliente,
                    numAsiento=asiento.asiento.numero,  # Aquí obtenemos el número de asiento
                    precio=asiento.precio,
                )
                asientos_actualizados.append(asiento_id)
            except ProgramacionAsiento.DoesNotExist:
                errores_asientos.append(asiento_id)

        # Generar la respuesta dependiendo de si hubo errores o no
        if errores_asientos:
            return Response(
                {
                    "message": "Algunos asientos no se pudieron vender.",
                    "asientos_no_vendidos": errores_asientos,
                    "asientos_vendidos": asientos_actualizados,
                },
                status=400,
            )

        return Response({"message": "Asiento/s comprados exitosamente."}, status=200)


class ReservarAsientoView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReservarAsientoSerializer(data=request.data)
        if serializer.is_valid():
            programacion_id = serializer.validated_data["programacion_viaje_id"]
            asientos_ids = serializer.validated_data["asientos_ids"]
            cliente = serializer.validated_data["cliente_id"]

            # Verificar asientos disponibles antes de actualizar
            asientos_disponibles = ProgramacionAsiento.objects.filter(
                programacionViaje_id=programacion_id,
                id__in=asientos_ids,
                estado="libre",
            )

            if asientos_disponibles.count() != len(asientos_ids):
                return Response(
                    {"error": "Uno o más asientos no están disponibles."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Actualizar el estado de los asientos a 'reservado'
            ProgramacionAsiento.objects.filter(
                programacionViaje_id=programacion_id, id__in=asientos_ids
            ).update(estado="reservado")

            # Crear registros de embarque para el cliente
            for asiento in asientos_disponibles:
                Embarque.objects.create(
                    programacionViaje_id=programacion_id,
                    pasajero_id=cliente,
                    numAsiento=asiento.id,
                    estado="reservado",
                )

            return Response(
                {"message": "Asientos reservados con éxito."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmbarqueViewSet(viewsets.ModelViewSet):
    queryset = Embarque.objects.all()
    serializer_class = EmbarqueSerializer


class ManifiestoViewSet(viewsets.ModelViewSet):
    queryset = Manifiesto.objects.all()
    serializer_class = ManifiestoSerializer

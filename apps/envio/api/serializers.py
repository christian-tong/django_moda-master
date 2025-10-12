# BCAKEND apps\envio\api\serializers.py
from rest_framework import serializers
from apps.envio.models import (
    Encomienda,
    Liquidacion,
    liquidacionRecepcion,
    ClienteRecepcion,
)
from apps.empresa.models import Agencia, Vehiculo, Conductor
from apps.persona.models import Persona


# ==========================================================
# 🔹 Serializadores Simples
# ==========================================================
class PersonaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ["id", "denominacion", "numDoc"]


class AgenciaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agencia
        fields = ["id", "nombre"]


class VehiculoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ["id", "placa", "marca"]


class ConductorSimpleSerializer(serializers.ModelSerializer):
    chofer = PersonaSimpleSerializer(read_only=True)

    class Meta:
        model = Conductor
        fields = ["id", "chofer", "numLicencia", "categoria"]


# ==========================================================
# 🔹 Encomienda
# ==========================================================
class EncomiendaListSerializer(serializers.ModelSerializer):
    remite = PersonaSimpleSerializer(read_only=True)
    consignado = PersonaSimpleSerializer(read_only=True)
    agenciaOrigen = AgenciaSimpleSerializer(read_only=True)
    agenciaDestino = AgenciaSimpleSerializer(read_only=True)

    # Fechas derivadas
    fechaCreacion = serializers.SerializerMethodField()
    fechaRecepcion = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            "id",
            "numDocumento",
            "remite",
            "consignado",
            "agenciaOrigen",
            "agenciaDestino",
            "esContraEntrega",
            "aDomicilio",
            "estado",
            "precio",
            "numeroContacto",
            "fechaCreacion",
            "fechaRecepcion",
        ]

    def get_fechaCreacion(self, obj):
        """Obtiene la fecha del movimiento de venta asociado (si existe)."""
        venta = getattr(obj, "venta", None)
        return venta.create if venta else None

    def get_fechaRecepcion(self, obj):
        """Obtiene la fecha de recepción del cliente (si existe)."""
        recepcion = getattr(obj, "clienterecepcion", None)
        return recepcion.fecha if recepcion else None


class EncomiendaDetailSerializer(EncomiendaListSerializer):
    class Meta(EncomiendaListSerializer.Meta):
        fields = EncomiendaListSerializer.Meta.fields + [
            "domicilio",
            "seguridadClave",
            "observacion",
        ]


class EncomiendaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encomienda
        fields = [
            "remite",
            "consignado",
            "agenciaOrigen",
            "agenciaDestino",
            "esContraEntrega",
            "aDomicilio",
            "domicilio",
            "seguridadClave",
            "observacion",
            "precio",
            "numeroContacto",
        ]


# ==========================================================
# 🔹 Liquidación
# ==========================================================
class LiquidacionListSerializer(serializers.ModelSerializer):
    agenciaOrigen = AgenciaSimpleSerializer(read_only=True)
    agenciaDestino = AgenciaSimpleSerializer(read_only=True)
    vehiculo = VehiculoSimpleSerializer(read_only=True)
    conductor = ConductorSimpleSerializer(read_only=True)

    class Meta:
        model = Liquidacion
        fields = [
            "id",
            "numDocumento",
            "agenciaOrigen",
            "agenciaDestino",
            "vehiculo",
            "conductor",
            "fecha",
            "finalizado",
        ]


class LiquidacionDetailSerializer(LiquidacionListSerializer):
    encomienda = EncomiendaListSerializer(many=True, read_only=True)

    class Meta(LiquidacionListSerializer.Meta):
        fields = LiquidacionListSerializer.Meta.fields + [
            "observacion",
            "encomienda",
        ]


class LiquidacionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liquidacion
        exclude = ["usuario", "fecha", "finalizado", "encomienda"]


# ==========================================================
# 🔹 Liquidación Recepción
# ==========================================================
class LiquidacionRecepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = liquidacionRecepcion
        fields = ["id", "usuario", "liquidacion", "fecha", "observacion"]


# ==========================================================
# 🔹 Cliente Recepción
# ==========================================================
class ClienteRecepcionSerializer(serializers.ModelSerializer):
    usuario = PersonaSimpleSerializer(read_only=True)
    encomienda = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClienteRecepcion
        fields = ["id", "encomienda", "usuario", "fecha", "evidencia"]

# apps/viaje/API/serializers.py
"""
Serializers para la app de viaje.
Divididos en List, Detail y Write para mantener consistencia
y claridad entre lectura y escritura.
"""

from rest_framework import serializers
from ..models import ProgramacionViaje, ProgramacionAsiento, Embarque, Manifiesto
from apps.empresa.models import Vehiculo, Conductor, Agencia, Asiento
from apps.persona.models import Persona
from apps.caja.models import MovimientoCaja  # 👈 necesario para verificar pago


# -----------------------------
# ProgramacionViaje
# -----------------------------
class ProgramacionViajeListSerializer(serializers.ModelSerializer):
    rutaOrigen = serializers.StringRelatedField()
    rutaDestino = serializers.StringRelatedField()
    vehiculo = serializers.StringRelatedField()

    class Meta:
        model = ProgramacionViaje
        fields = [
            "id",
            "nombreViaje",
            "rutaOrigen",
            "rutaDestino",
            "fechaViaje",
            "horaViaje",
            "vehiculo",
            "precio",
            "activo",
        ]


class ProgramacionViajeDetailSerializer(serializers.ModelSerializer):
    rutaOrigen = serializers.StringRelatedField()
    rutaDestino = serializers.StringRelatedField()
    vehiculo = serializers.StringRelatedField()
    piloto = serializers.StringRelatedField()
    copiloto = serializers.StringRelatedField()
    ayudante = serializers.StringRelatedField()
    terramosa = serializers.StringRelatedField()

    class Meta:
        model = ProgramacionViaje
        fields = "__all__"


class ProgramacionViajeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionViaje
        fields = "__all__"


# -----------------------------
# ProgramacionAsiento
# -----------------------------
class ProgramacionAsientoSerializer(serializers.ModelSerializer):
    asiento = serializers.StringRelatedField()

    class Meta:
        model = ProgramacionAsiento
        fields = ["id", "programacionViaje", "asiento", "estado", "precio"]


class ProgramacionAsientoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionAsiento
        fields = "__all__"


# -----------------------------
# Embarque
# -----------------------------
class EmbarqueListSerializer(serializers.ModelSerializer):
    pasajero = serializers.StringRelatedField()
    programacionViaje = serializers.StringRelatedField()
    pagado = serializers.SerializerMethodField()  # 👈 campo adicional

    class Meta:
        model = Embarque
        fields = [
            "id",
            "numDocumento",
            "programacionViaje",
            "pasajero",
            "numAsiento",
            "precio",
            "enSala",
            "telefono",
            "create",
            "pagado",  # 👈 ahora se expone
        ]

    def get_pagado(self, obj: Embarque):
        if not obj.venta_id:
            return False
        return MovimientoCaja.objects.filter(venta=obj.venta).exists()


class EmbarqueDetailSerializer(serializers.ModelSerializer):
    pasajero = serializers.StringRelatedField()
    lugar_abordo = serializers.StringRelatedField()
    lugar_bajada = serializers.StringRelatedField()
    programacionViaje = serializers.StringRelatedField()
    pagado = serializers.SerializerMethodField()  # 👈 también en detail

    class Meta:
        model = Embarque
        fields = "__all__"

    def get_pagado(self, obj: Embarque):
        if not obj.venta_id:
            return False
        return MovimientoCaja.objects.filter(venta=obj.venta).exists()


# --- EmbarqueWriteSerializer: valida y bloquea numDocumento en update ---
class EmbarqueWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embarque
        fields = "__all__"

    def update(self, instance, validated_data):
        # numDocumento es inmutable
        if (
            "numDocumento" in validated_data
            and validated_data["numDocumento"] != instance.numDocumento
        ):
            raise serializers.ValidationError(
                {
                    "numDocumento": "No se permite modificar el número de documento una vez emitido."
                }
            )
        return super().update(instance, validated_data)


# -----------------------------
# Manifiesto
# -----------------------------
class ManifiestoListSerializer(serializers.ModelSerializer):
    programacionViaje = serializers.StringRelatedField()

    class Meta:
        model = Manifiesto
        fields = [
            "id",
            "numDocumento",
            "fechaViaje",
            "vehiculo",
            "programacionViaje",
            "seGenero",
        ]


class ManifiestoDetailSerializer(serializers.ModelSerializer):
    programacionViaje = ProgramacionViajeDetailSerializer(read_only=True)
    embarque = EmbarqueListSerializer(many=True, read_only=True)

    class Meta:
        model = Manifiesto
        fields = "__all__"


class ManifiestoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifiesto
        fields = "__all__"

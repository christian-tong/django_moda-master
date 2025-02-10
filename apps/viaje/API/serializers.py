from rest_framework import serializers

from ..models import ProgramacionViaje, ProgramacionAsiento, Embarque, Manifiesto


class ProgramacionViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionViaje
        fields = "__all__"


class ProgramacionAsientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionAsiento
        fields = "__all__"


class AsientosDisponiblesSerializer(serializers.Serializer):
    libres = ProgramacionAsientoSerializer(many=True)
    vendidos = ProgramacionAsientoSerializer(many=True)


class ReservarAsientoSerializer(serializers.Serializer):
    programacion_viaje_id = serializers.IntegerField()
    asientos_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    nro_documento = serializers.CharField(
        max_length=20, required=True
    )  # Campo adicional

    def validate(self, data):
        # Verificar que los asientos están disponibles
        programacion_viaje_id = data.get("programacion_viaje_id")
        asientos_ids = data.get("asientos_ids")

        asientos_disponibles = ProgramacionAsiento.objects.filter(
            programacionViaje_id=programacion_viaje_id,
            id__in=asientos_ids,
            estado="libre",
        )

        if asientos_disponibles.count() != len(asientos_ids):
            raise serializers.ValidationError(
                "Uno o más asientos no están disponibles."
            )

        return data


class EmbarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embarque
        fields = "__all__"


class ManifiestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifiesto
        fields = "__all__"

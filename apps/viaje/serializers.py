from rest_framework import serializers
from .models import ProgramacionViaje, ProgramacionAsiento, Embarque, Manifiesto


class ProgramacionViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionViaje
        fields = "__all__"


class ProgramacionAsientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionAsiento
        fields = "__all__"


class EmbarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embarque
        fields = "__all__"


class ManifiestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifiesto
        fields = "__all__"


class ReservarAsientoSerializer(serializers.Serializer):
    programacion_viaje_id = serializers.IntegerField()
    asientos_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )

    def validate(self, data):
        programacion_id = data.get("programacion_viaje_id")
        asientos_ids = data.get("asientos_ids")

        # Verificar si los asientos están disponibles
        asientos = ProgramacionAsiento.objects.filter(
            programacionViaje_id=programacion_id,
            asiento_id__in=asientos_ids,
            estado="libre",
        )
        if len(asientos) != len(asientos_ids):
            raise serializers.ValidationError(
                "Uno o más asientos no están disponibles."
            )
        return data

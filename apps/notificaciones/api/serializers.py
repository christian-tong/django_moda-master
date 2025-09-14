from rest_framework import serializers
from ..models import RegistroCumpleanos


class RegistroCumpleanosSerializer(serializers.ModelSerializer):
    persona_nombre = serializers.CharField(source="persona.nombres", read_only=True)
    persona_apellido = serializers.CharField(source="persona.apellidoP", read_only=True)

    class Meta:
        model = RegistroCumpleanos
        fields = [
            "id",
            "persona",
            "persona_nombre",
            "persona_apellido",
            "correo",
            "fecha_envio",
            "mensaje",
            "promo",
            "enviado",
        ]

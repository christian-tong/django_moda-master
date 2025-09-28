# BACKEND apps\catalogoSunat\api\serializers.py

from rest_framework import serializers
from apps.catalogoSunat.models import Ubigeo


class UbigeoSerializer(serializers.ModelSerializer):
    """
    Serializer básico para Ubigeo con un campo amigable `nombreCompleto`.
    Compatible con el front (usa nombreCompleto en vez de concatenar en React).
    """

    nombreCompleto = serializers.SerializerMethodField()

    class Meta:
        model = Ubigeo
        fields = [
            "id",
            "codigo",
            "distrito",
            "provincia",
            "departamento",
            "nombreCompleto",
        ]

    def get_nombreCompleto(self, obj):
        return obj.ubigeo_completo()

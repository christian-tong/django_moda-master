# BACKEND apps\facturacion\api\serializers.py

from rest_framework import serializers
from apps.facturacion.models import FaturaBoleta
from apps.persona.models import Persona
from apps.catalogoSunat.models import TipoDocumento
from apps.venta.models import Movimiento


class FaturaBoletaListSerializer(serializers.ModelSerializer):
    tipoDocumento = serializers.StringRelatedField()
    cliente = serializers.StringRelatedField()

    class Meta:
        model = FaturaBoleta
        fields = [
            "id",
            "tipoDocumento",
            "serie",
            "numero",
            "cliente",
            "monto",
            "fechaFact",
            "estaFacturado",
        ]


class FaturaBoletaDetailSerializer(serializers.ModelSerializer):
    tipoDocumento = serializers.StringRelatedField()
    cliente = serializers.StringRelatedField()
    usuario = serializers.StringRelatedField()
    ventaMovimiento = serializers.StringRelatedField()

    class Meta:
        model = FaturaBoleta
        fields = "__all__"


class FaturaBoletaWriteSerializer(serializers.ModelSerializer):
    tipoDocumento = serializers.PrimaryKeyRelatedField(
        queryset=TipoDocumento.objects.all()
    )
    cliente = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(), allow_null=True, required=False
    )
    ventaMovimiento = serializers.PrimaryKeyRelatedField(
        queryset=Movimiento.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = FaturaBoleta
        fields = "__all__"

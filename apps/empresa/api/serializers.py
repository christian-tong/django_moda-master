# region Imports
from rest_framework import serializers
from apps.empresa.models import (
    Conductor,
    Agencia,
    AgenciaDocumento,
    Ruta,
    Vehiculo,
    Asiento,
)
from apps.persona.models import Persona
from apps.catalogoSunat.models import Ubigeo, TipoDocumento

# endregion


# region PersonaSimpleSerializer
class PersonaSimpleSerializer(serializers.ModelSerializer):
    """
    /// <summary>
    /// Serializer ligero para mostrar referencia a Persona (como en autocomplete).
    /// </summary>
    """

    class Meta:
        model = Persona
        fields = ["id", "denominacion"]


# endregion


# region UbigeoSimpleSerializer
class UbigeoSimpleSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = Ubigeo
        fields = ["id", "codigo", "nombre"]

    def get_nombre(self, obj):
        # 👇 concatenamos un string amigable
        return f"{obj.distrito} - {obj.provincia} - {obj.departamento}"


# endregion


# region TipoDocumentoSimpleSerializer
class TipoDocumentoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ["id", "codigo", "descripcion"]


# endregion


# region ConductorSerializers
class ConductorListSerializer(serializers.ModelSerializer):
    chofer = PersonaSimpleSerializer(read_only=True)

    class Meta:
        model = Conductor
        fields = [
            "id",
            "chofer",
            "numLicencia",
            "clase",
            "categoria",
            "fechaExpedicion",
            "fechaRevalidacion",
            "activo",
        ]


class ConductorDetailSerializer(serializers.ModelSerializer):
    chofer = PersonaSimpleSerializer(read_only=True)

    class Meta:
        model = Conductor
        fields = [
            "id",
            "chofer",
            "numLicencia",
            "clase",
            "categoria",
            "fechaExpedicion",
            "fechaRevalidacion",
            "activo",
        ]


class ConductorWriteSerializer(serializers.ModelSerializer):
    chofer = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all())

    class Meta:
        model = Conductor
        fields = [
            "chofer",
            "numLicencia",
            "clase",
            "categoria",
            "fechaExpedicion",
            "fechaRevalidacion",
            "activo",
        ]


# endregion


# region AgenciaSerializers
class AgenciaListSerializer(serializers.ModelSerializer):
    ubigeo = UbigeoSimpleSerializer(read_only=True)
    responsable = PersonaSimpleSerializer(read_only=True)
    empresa = PersonaSimpleSerializer(read_only=True)

    class Meta:
        model = Agencia
        fields = [
            "id",
            "nombre",
            "ubigeo",
            "responsable",
            "empresa",
            "direccion",
            "fijo",
            "movilUno",
            "movilDos",
            "correo",
            "tipo",
            "activo",
            "codigoSerieDocumento",
            "isruta",
            "foto",
        ]


class AgenciaDetailSerializer(AgenciaListSerializer):
    foto = serializers.ImageField(read_only=True)

    class Meta(AgenciaListSerializer.Meta):
        fields = AgenciaListSerializer.Meta.fields + ["foto"]


class AgenciaWriteSerializer(serializers.ModelSerializer):
    ubigeo = serializers.PrimaryKeyRelatedField(queryset=Ubigeo.objects.all())
    responsable = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Agencia
        exclude = ["empresa", "tipo"]


# endregion


# region Otros
class AgenciaDocumentoSerializer(serializers.ModelSerializer):
    documento = TipoDocumentoSimpleSerializer(read_only=True)

    class Meta:
        model = AgenciaDocumento
        fields = ["id", "agencia", "documento", "serie", "correlativo", "activo"]


# endregion


# region VehiculoSerializers
class VehiculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = [
            "id",
            "placa",
            "categoria",
            "marca",
            "modelo",
            "color",
            "numSerie",
            "numMotor",
            "carroceria",
            "combustible",
            "numAsientos",
            "numPasajeros",
            "propio",
            "numfilas",
            "numColumnas",
        ]


class VehiculoDetailSerializer(VehiculoListSerializer):
    pass


class VehiculoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = "__all__"


# endregion


# region AsientoSerializers
class AsientoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asiento
        fields = [
            "id",
            "vehiculo",
            "codigoMatrix",
            "numero",
            "saltofila",
            "estado",
        ]


class AsientoDetailSerializer(AsientoListSerializer):
    vehiculo = VehiculoListSerializer(read_only=True)


class AsientoWriteSerializer(serializers.ModelSerializer):
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all())

    class Meta:
        model = Asiento
        fields = [
            "vehiculo",
            "codigoMatrix",
            "numero",
            "saltofila",
            "estado",
        ]


# endregion


# region RutaSerializers
class AgenciaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agencia
        fields = ["id", "nombre"]


class RutaSerializer(serializers.ModelSerializer):
    origen = AgenciaSimpleSerializer(read_only=True)
    destino = AgenciaSimpleSerializer(read_only=True)
    km_promedio = serializers.DecimalField(
        source="distancia_km", max_digits=6, decimal_places=2, required=False
    )
    tiempo_promedio = serializers.DurationField(
        source="duracion_aprox", required=False, allow_null=True
    )

    class Meta:
        model = Ruta
        fields = ["id", "origen", "destino", "km_promedio", "tiempo_promedio", "activo"]


class RutaWriteSerializer(serializers.ModelSerializer):
    km_promedio = serializers.DecimalField(
        source="distancia_km", max_digits=6, decimal_places=2, required=False, default=0
    )
    tiempo_promedio = serializers.DurationField(
        source="duracion_aprox", required=False, allow_null=True
    )

    class Meta:
        model = Ruta
        fields = ["id", "origen", "destino", "km_promedio", "tiempo_promedio", "activo"]


# endregion

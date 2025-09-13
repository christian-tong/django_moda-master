# region Imports
from rest_framework import serializers
from apps.empresa.models import Conductor, Agencia, AgenciaDocumento, Vehiculo, Asiento
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
    class Meta:
        model = Ubigeo
        fields = ["id", "codigo", "nombre"]


# endregion


# region TipoDocumentoSimpleSerializer
class TipoDocumentoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ["id", "codigo", "descripcion"]


# endregion


# region ConductorSerializers
class ConductorListSerializer(serializers.ModelSerializer):
    """
    /// <summary>
    /// Listado ligero de conductores.
    /// Mantiene clave 'chofer' como objeto simple (id + denominacion).
    /// </summary>
    """

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
    """
    /// <summary>
    /// Escritura: acepta 'chofer' como PK de Persona.
    /// </summary>
    """

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
        ]


class AgenciaDetailSerializer(AgenciaListSerializer):
    foto = serializers.ImageField(read_only=True)


class AgenciaWriteSerializer(serializers.ModelSerializer):
    """
    /// <summary>
    /// Escritura: ubigeo y responsable como PKs; 'empresa' no se espera en create (se asigna automáticamente en create como en la vista original).
    /// </summary>
    """

    ubigeo = serializers.PrimaryKeyRelatedField(queryset=Ubigeo.objects.all())
    responsable = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(), allow_null=True, required=False
    )
    empresa = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Agencia
        # reproducimos el exclude = ["empresa", "tipo"] del formulario original:
        exclude = ["empresa", "tipo"]
        # si prefieres lista explícita, reemplaza por fields = [...]


# endregion


# region Otros (opcional)
class AgenciaDocumentoSerializer(serializers.ModelSerializer):
    documento = TipoDocumentoSimpleSerializer(read_only=True)

    class Meta:
        model = AgenciaDocumento
        fields = ["id", "agencia", "documento", "serie", "correlativo", "activo"]


# endregion

# BACKEND apps/persona/API/serializers.py
"""
Serializers para la app de persona.
Separados en List, Detail y Write para mayor claridad.
"""
from rest_framework import serializers
from ..models import Persona, PersonaNatural, PersonaJuridica


# -----------------------------
# Persona
# -----------------------------
class PersonaListSerializer(serializers.ModelSerializer):
    tipoDoc = serializers.StringRelatedField()

    class Meta:
        model = Persona
        fields = ["id", "numDoc", "denominacion", "tipoDoc", "activo", "ispersonal"]


class PersonaDetailSerializer(serializers.ModelSerializer):
    tipoDoc = serializers.StringRelatedField()
    # 🔥 Incluir datos de PersonaNatural
    nombres = serializers.CharField(
        source="personanatural.nombres", allow_blank=True, required=False
    )
    apellidoP = serializers.CharField(
        source="personanatural.apellidoP", allow_blank=True, required=False
    )
    apellidoM = serializers.CharField(
        source="personanatural.apellidoM", allow_blank=True, required=False
    )
    fechaNac = serializers.DateField(
        source="personanatural.fechaNac", allow_null=True, required=False
    )
    genero = serializers.CharField(
        source="personanatural.genero", allow_blank=True, required=False
    )

    class Meta:
        model = Persona
        fields = "__all__"


class PersonaWriteSerializer(serializers.ModelSerializer):
    # 🔥 También permitir escribir campos de PersonaNatural
    nombres = serializers.CharField(write_only=True, required=False, allow_blank=True)
    apellidoP = serializers.CharField(write_only=True, required=False, allow_blank=True)
    apellidoM = serializers.CharField(write_only=True, required=False, allow_blank=True)
    fechaNac = serializers.DateField(write_only=True, required=False, allow_null=True)
    genero = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Persona
        fields = "__all__"  # incluye todos los de Persona + los extras arriba
        extra_kwargs = {
            "movilUno": {"required": False, "allow_null": True},
            "movilDos": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        # Sacar datos de PersonaNatural
        nombres = validated_data.pop("nombres", "")
        apellidoP = validated_data.pop("apellidoP", "")
        apellidoM = validated_data.pop("apellidoM", "")
        fechaNac = validated_data.pop("fechaNac", None)
        genero = validated_data.pop("genero", "")

        persona = Persona.objects.create(**validated_data)

        # Crear PersonaNatural vinculada
        PersonaNatural.objects.create(
            persona=persona,
            nombres=nombres,
            apellidoP=apellidoP,
            apellidoM=apellidoM,
            fechaNac=fechaNac,
            genero=genero,
        )
        return persona

    def update(self, instance, validated_data):
        # Sacar datos de PersonaNatural
        nombres = validated_data.pop("nombres", None)
        apellidoP = validated_data.pop("apellidoP", None)
        apellidoM = validated_data.pop("apellidoM", None)
        fechaNac = validated_data.pop("fechaNac", None)
        genero = validated_data.pop("genero", None)

        # Actualizar Persona
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Crear/Actualizar PersonaNatural
        pn, _ = PersonaNatural.objects.get_or_create(persona=instance)
        if nombres is not None:
            pn.nombres = nombres
        if apellidoP is not None:
            pn.apellidoP = apellidoP
        if apellidoM is not None:
            pn.apellidoM = apellidoM
        if fechaNac is not None:
            pn.fechaNac = fechaNac
        if genero is not None:
            pn.genero = genero
        pn.save()

        return instance


# -----------------------------
# PersonaNatural
# -----------------------------
class PersonaNaturalSerializer(serializers.ModelSerializer):
    persona = PersonaDetailSerializer(read_only=True)

    class Meta:
        model = PersonaNatural
        fields = "__all__"


class PersonaNaturalWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaNatural
        exclude = ["persona"]


# -----------------------------
# PersonaJuridica
# -----------------------------
class PersonaJuridicaSerializer(serializers.ModelSerializer):
    persona = PersonaDetailSerializer(read_only=True)

    class Meta:
        model = PersonaJuridica
        fields = "__all__"


class PersonaJuridicaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaJuridica
        exclude = ["persona"]

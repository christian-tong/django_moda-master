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

    class Meta:
        model = Persona
        fields = "__all__"


class PersonaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = "__all__"


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

from rest_framework import serializers
from .models import Persona, PersonaNatural, PersonaJuridica


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = "__all__"


class PersonaNaturalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaNatural
        fields = "__all__"


class PersonaJuridicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaJuridica
        fields = "__all__"


class PersonaSerializerAPI(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = "__all__"  # Asegúrate de incluir 'id' si no usas "__all__"


class PersonaNaturalSerializerAPI(serializers.ModelSerializer):
    persona = PersonaSerializer()
    foto = serializers.ImageField(
        required=False, allow_null=True
    )  # Hacer opcional la foto

    class Meta:
        model = PersonaNatural
        fields = [
            "persona",
            "nombres",
            "apellidoP",
            "apellidoM",
            "fechaNac",
            "foto",
            "genero",
        ]

    def create(self, validated_data):
        # Extraer datos de persona
        persona_data = validated_data.pop("persona")
        # Crear la instancia de Persona
        persona = Persona.objects.create(**persona_data)
        # Crear la instancia de PersonaNatural
        persona_natural = PersonaNatural.objects.create(
            persona=persona, **validated_data
        )
        return persona_natural

    def update(self, instance, validated_data):
        # Manejar datos relacionados con Persona
        persona_data = validated_data.pop("persona", None)
        if persona_data:
            for key, value in persona_data.items():
                setattr(instance.persona, key, value)
            instance.persona.save()

        # Actualizar datos de PersonaNatural
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class PersonaJuridicaSerializerAPI(serializers.ModelSerializer):
    persona = PersonaSerializer()

    class Meta:
        model = PersonaJuridica
        fields = ["persona", "estado", "condicion"]

    def create(self, validated_data):
        # Extraer datos de persona
        persona_data = validated_data.pop("persona")
        # Crear la instancia de Persona
        persona = Persona.objects.create(**persona_data)
        # Crear la instancia de PersonaJuridica
        persona_juridica = PersonaJuridica.objects.create(
            persona=persona, **validated_data
        )
        return persona_juridica

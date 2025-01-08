from rest_framework import serializers
from .models import Persona, PersonaNatural, PersonaJuridica

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class PersonaNaturalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaNatural
        fields = '__all__'

class PersonaJuridicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaJuridica
        fields = '__all__'

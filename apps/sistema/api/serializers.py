from rest_framework import serializers
from ..models import Usuario, Menu
from apps.empresa.models import Agencia
from apps.persona.models import Persona

class UsuarioSerializer(serializers.ModelSerializer):
    persona = serializers.StringRelatedField()
    agencia = serializers.StringRelatedField(many=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "is_active", "persona", "agencia"]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = Usuario(
            username=validated_data["username"],
            email=validated_data.get("email", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"

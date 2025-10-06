from rest_framework import serializers
from ..models import Usuario, Menu
from apps.empresa.models import Agencia
from apps.persona.models import Persona


class UsuarioSerializer(serializers.ModelSerializer):
    # 🔹 nombres legibles
    agencias = serializers.SlugRelatedField(
        many=True,
        slug_field="nombre",
        read_only=True,
        source="agencia",
    )

    # 🔹 IDs (para lectura y escritura)
    agencia_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Agencia.objects.all(),
        source="agencia",
        required=False,
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "persona",
            "persona_id",
            "agencias",  # nombres
            "agencia_ids",  # IDs ahora visibles también al GET
            "date_joined",
            "last_login",
        ]

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = Usuario(
            username=validated_data["username"], email=validated_data.get("email", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"

from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from apps.persona.models import Persona
from apps.empresa.models import Agencia


class Usuario(AbstractUser):
    persona = models.OneToOneField(
        Persona,
        db_column="persona_id",
        null=True,
        blank=True,
        related_name="persona_usuario",
        on_delete=models.PROTECT,
    )

    agencia = models.ManyToManyField(
        Agencia, related_name="agencia_usuario", blank=True
    )

    def __str__(self):
        return self.username


class Menu(models.Model):
    nombre = models.CharField(verbose_name="Nombre del menu", max_length=50)
    url = models.CharField(max_length=30, blank=True, null=True)
    icono = models.CharField(max_length=20, blank=True, null=True)
    permiso = models.ForeignKey(
        Permission, on_delete=models.CASCADE, blank=True, null=True
    )
    padre = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    orden = models.SmallIntegerField(blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True, default=True)

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        permissions = [
            ("tesoreria_menu", "Can view menu tesoreria"),
            ("viajes_menu", "Can view menu Viajes"),
            ("envios_menu", "Can view menu envios"),
            ("facturacion_menu", "Can view menu Facturacion"),
            ("reportes_menu", "Can view menu Reportes"),
            ("personas_menu", "Can view menu Personas"),
            ("empresa_menu", "Can view menu empresa"),
            ("sistema_menu", "Can view menu Sistema"),
        ]

    def __str__(self):
        return self.nombre

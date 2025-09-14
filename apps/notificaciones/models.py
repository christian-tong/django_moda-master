# apps/notificaciones/models.py

from django.db import models
from apps.persona.models import PersonaNatural
from django.utils.timezone import now


class RegistroCumpleanos(models.Model):
    """
    Guarda los correos de cumpleaños enviados.
    Permite saber a quién ya se le envió para evitar duplicados.
    """

    persona = models.ForeignKey(
        PersonaNatural, on_delete=models.CASCADE, related_name="cumpleanos_registros"
    )
    correo = models.EmailField()
    fecha_envio = models.DateTimeField(default=now)
    mensaje = models.TextField(blank=True, null=True)
    promo = models.TextField(blank=True, null=True)
    enviado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Registro de cumpleaños"
        verbose_name_plural = "Registros de cumpleaños"
        unique_together = ("persona", "fecha_envio")

    def __str__(self):
        return f"{self.persona.nombres} {self.persona.apellidoP} ({self.correo})"

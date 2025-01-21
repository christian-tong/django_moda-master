from django.db import models
from apps.persona.models import Persona
from apps.empresa.models import Agencia


class Movimiento(models.Model):
    vendedor = models.ForeignKey(Persona, on_delete=models.CASCADE)
    agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"

    def __str__(self):
        return self.vendedor.denominacion


class DetalleMov(models.Model):
    movimiento = models.ForeignKey(
        Movimiento, on_delete=models.PROTECT, blank=True, null=True
    )
    unidadMedida = models.CharField(
        max_length=20, choices=[("NIU", "Unidad"), ("ZZ", "Servicio")], default="ZZ"
    )
    cantidad = models.DecimalField(
        verbose_name="Cantidad", max_digits=5, decimal_places=2, default=1
    )
    descripcion = models.TextField()
    valorUnitario = models.DecimalField(max_digits=8, decimal_places=2)
    subTotal = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )

    class Meta:
        verbose_name = "DetalleMov"
        verbose_name_plural = "DetalleMovs"

    def __str__(self):
        return self.descripcion

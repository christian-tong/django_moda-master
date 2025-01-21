import os
from datetime import datetime
from django.db import models
from apps.venta.models import Movimiento
from apps.persona.models import Persona
from apps.empresa.models import Agencia, Vehiculo, Conductor

ESTADO = [
    ("agenciaOrigen", "Agencia de origen"),
    ("enCamino", "Enviado en camino"),
    ("agenciaDestino", "Listo para Recoger"),
    ("recepcionado", "Entrega Exitosa"),
]


class Encomienda(models.Model):
    ##recepcion se gurad en movimiento
    numDocumento = models.CharField(max_length=8, blank=True, null=True)
    venta = models.OneToOneField(
        Movimiento, on_delete=models.PROTECT, blank=True, null=True
    )
    remite = models.ForeignKey(
        Persona, on_delete=models.PROTECT, related_name="remite_persona"
    )
    consignado = models.ForeignKey(
        Persona, on_delete=models.PROTECT, related_name="consignado_persona"
    )
    agenciaOrigen = models.ForeignKey(Agencia, on_delete=models.PROTECT)
    agenciaDestino = models.ForeignKey(
        Agencia, on_delete=models.PROTECT, related_name="destino_agencia"
    )
    esContraEntrega = models.BooleanField(
        verbose_name="¿Contra entrega?", default=False
    )  # es = true no es=false
    aDomicilio = models.BooleanField(verbose_name="¿A domicilio?", default=False)
    domicilio = models.CharField(
        max_length=200, verbose_name="Direccion del domicilio", blank=True, null=True
    )
    seguridadClave = models.CharField(max_length=4)
    observacion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO, blank=True, null=True)
    precio = models.DecimalField(
        max_digits=7, decimal_places=2, default=0, blank=True, null=True
    )
    numeroContacto = models.CharField(
        verbose_name="Telefono", max_length=50, blank=True, null=True
    )

    class Meta:
        verbose_name = "Encomienda"
        verbose_name_plural = "Encomiendas"

    def __str__(self):
        return str(self.id)


def rutaNombreImagen(instance, filename):
    extencion = os.path.splitext(filename)[1][1:]
    fecha = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    return f"encomienda/{instance.encomienda.id}-{fecha}." + extencion


class ClienteRecepcion(models.Model):
    encomienda = models.OneToOneField(
        Encomienda, on_delete=models.PROTECT, blank=True, null=True
    )
    usuario = models.ForeignKey(
        Persona, on_delete=models.PROTECT, blank=True, null=True
    )
    fecha = models.DateTimeField(auto_now=True)
    evidencia = models.ImageField(upload_to=rutaNombreImagen, blank=True, null=True)

    class Meta:
        verbose_name = "ClienteRecepcion"
        verbose_name_plural = "ClienteRecepcions"

    def __str__(self):
        return self.encomienda.domicilio


class Liquidacion(models.Model):
    numDocumento = models.IntegerField(blank=True, null=True)
    usuario = models.ForeignKey(
        Persona, on_delete=models.PROTECT, blank=True, null=True
    )
    agenciaOrigen = models.ForeignKey(Agencia, on_delete=models.PROTECT)
    agenciaDestino = models.ForeignKey(
        Agencia, on_delete=models.PROTECT, related_name="agencia_destino"
    )
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    conductor = models.ForeignKey(Conductor, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now=True)
    observacion = models.TextField(blank=True, null=True)
    finalizado = models.BooleanField(default=False)
    encomienda = models.ManyToManyField(Encomienda)

    class Meta:
        verbose_name = "Liquidacion"
        verbose_name_plural = "Liquidacions"

    def __str__(self):
        return str(self.id)


class liquidacionRecepcion(models.Model):
    usuario = models.ForeignKey(
        Persona, on_delete=models.PROTECT, blank=True, null=True
    )
    liquidacion = models.OneToOneField(
        Liquidacion, on_delete=models.PROTECT, blank=True, null=True
    )
    fecha = models.DateTimeField(auto_now=True)
    observacion = models.TextField()

    class Meta:
        verbose_name = "liquidacionRecepcion"
        verbose_name_plural = "liquidacionRecepcions"

    def __str__(self):
        return str(self.id)

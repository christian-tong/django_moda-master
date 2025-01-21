from django.db import models
from django.forms import model_to_dict
from apps.persona.models import Persona
from apps.catalogoSunat.models import Ubigeo, TipoDocumento


class Vehiculo(models.Model):
    placa = models.CharField(max_length=10)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    numSerie = models.CharField(max_length=50, blank=True, null=True)
    numMotor = models.CharField(max_length=50, blank=True, null=True)
    carroceria = models.CharField(max_length=50, blank=True, null=True)
    combustible = models.CharField(max_length=100, blank=True, null=True)
    numAsientos = models.IntegerField(blank=True, null=True)
    numPasajeros = models.IntegerField(blank=True, null=True)
    propio = models.BooleanField(default=False)
    numfilas = models.SmallIntegerField(blank=True, null=True, default=1)
    numColumnas = models.SmallIntegerField(blank=True, null=True, default=1)

    class Meta:
        verbose_name = "Vehiculo"
        verbose_name_plural = "Vehiculos"

    def __str__(self):
        return self.placa


Estado = {
    ("libre", "Libre"),
    ("cortesia", "Cortesía"),
    ("pasadiso", "Pasadiso"),
}


class Asiento(models.Model):
    codigoMatrix = models.SmallIntegerField(default=1)
    numero = models.CharField(
        verbose_name="Numero de asiento", max_length=2, blank=True, null=True
    )
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    saltofila = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=20, null=True, blank=True, choices=Estado, default="libre"
    )

    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"

    def __str__(self):
        return str(self.codigoMatrix)

    def toJson(self):
        return model_to_dict(self)


class Conductor(models.Model):
    chofer = models.ForeignKey(Persona, on_delete=models.CASCADE)
    numLicencia = models.CharField(verbose_name="Nro de licencia", max_length=12)
    clase = models.CharField(max_length=1)
    categoria = models.CharField(max_length=5)
    fechaExpedicion = models.DateField(
        verbose_name="Fecha de expedición", blank=True, null=True
    )
    fechaRevalidacion = models.DateField(
        verbose_name="Fecha de revalidación", blank=True, null=True
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Conductor"
        verbose_name_plural = "Conductors"

    def __str__(self):
        return self.chofer.denominacion


TIPO = (
    ("PRINCIPAL", "PRINCIPAL"),
    ("SUCURSAL", "SUCURSAL"),
)


class Agencia(models.Model):
    nombre = models.CharField(max_length=150, blank=True, null=True)
    ubigeo = models.ForeignKey(Ubigeo, on_delete=models.CASCADE)
    responsable = models.ForeignKey(
        Persona, on_delete=models.CASCADE, blank=True, null=True
    )
    empresa = models.ForeignKey(
        Persona,
        related_name="empresa_agencia",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fijo = models.CharField(max_length=9, blank=True, null=True)
    movilUno = models.CharField(
        verbose_name="Celular", max_length=9, blank=True, null=True
    )
    movilDos = models.CharField(max_length=9, blank=True, null=True)
    correo = models.EmailField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO, blank=True, null=True)
    foto = models.ImageField(upload_to="media/agencia", blank=True, null=True)
    activo = models.BooleanField(default=True)
    codigoSerieDocumento = models.CharField(max_length=3, blank=True, null=True)
    isruta = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Agencia"
        verbose_name_plural = "Agencia"

    def __str__(self):
        return self.nombre


class AgenciaDocumento(models.Model):
    agencia = models.ForeignKey(Agencia, on_delete=models.PROTECT)
    documento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    serie = models.CharField(max_length=4)
    correlativo = models.IntegerField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AgenciaDocumento"
        verbose_name_plural = "AgenciaDocumentos"

    def __str__(self):
        return self.documento.descripcion

    def correlativoMas(self):
        correlativo = self.correlativo
        self.correlativo += 1
        self.save(update_fields=["correlativo"])
        return correlativo

    def correlativoMenos(self):
        correlativo = self.correlativo
        self.correlativo -= 1
        self.save(update_fields=["correlativo"])
        return correlativo

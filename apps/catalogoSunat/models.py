from django.db import models
from django.forms import model_to_dict


# catalogo01
class TipoDocumento(models.Model):
    codigo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=100)
    codOse = models.CharField(max_length=4, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "TipoDocumento"
        verbose_name_plural = "TipoDocumentos"

    def __str__(self):
        return self.descripcion


# catalogo 02 | Iso 4217
class TipoMoneda(models.Model):
    codigo = models.CharField(max_length=5)
    nomMoneda = models.CharField(max_length=50)
    codOse = models.IntegerField(blank=True, null=True)
    pais = models.CharField(max_length=50)
    tipoCambio = models.DecimalField(max_digits=4, decimal_places=3)

    class Meta:
        verbose_name = "TipoMoneda"
        verbose_name_plural = "TipoMonedas"

    def __str__(self):
        return self.codigo


# catalogo 06
class TipoDocumentoIdentidad(models.Model):
    codigo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=50)
    codOse = models.CharField(max_length=4, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "TipoDocumentoIdentidad"
        verbose_name_plural = "TipoDocumentoIdentidad"

    def __str__(self):
        return self.descripcion

    def toJSON(self):
        item = model_to_dict(self)
        return item


# catalo 07
class TipoAfectacionIgv(models.Model):
    codigo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=50)
    codTributo = models.CharField(max_length=8)
    codOse = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "TipoAfectacionIgv"
        verbose_name_plural = "TipoAfectacionIgv"

    def __str__(self):
        return self.descripcion


# catalogo 09
class TipoNotaCredito(models.Model):
    codigo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=50)
    codOse = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "TipoNotaCredito"
        verbose_name_plural = "TipoNotaCreditos"

    def __str__(self):
        return self.descripcion


# catalogo 10
class TipoNotaDebito(models.Model):
    codigo = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=50)
    codOse = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "TipoNotaDebito"
        verbose_name_plural = "TipoNotaDebito"

    def __str__(self):
        return self.descripcion


# catalogo 13 -INEI
class Ubigeo(models.Model):
    codigo = models.CharField(verbose_name="Ubigeo", max_length=8)
    distrito = models.CharField(max_length=255)
    provincia = models.CharField(max_length=255)
    departamento = models.CharField(max_length=255)
    numPoblacion = models.CharField(max_length=20, blank=True, null=True)
    superficie = models.CharField(max_length=20, blank=True, null=True)
    cordY = models.CharField(max_length=20, blank=True, null=True)
    cordX = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Ubigeo"
        verbose_name_plural = "Ubigeos"

    def __str__(self):
        return self.ubigeo_completo()

    def ubigeo_completo(self):
        return f"{self.distrito} - {self.provincia} - {self.departamento}"

    def toJSON(self):
        item = model_to_dict(self)
        # item['tipoDoc'] = self.tipoDoc.toJSON()
        return item


# catalogo 51
class TipoOperacion(models.Model):
    codigo = models.CharField(max_length=4)
    descripcion = models.CharField(max_length=50)
    codOse = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "TipoOperacion"
        verbose_name_plural = "TipoOperacion"

    def __str__(self):
        return self.codigo

from django.db import models
from apps.persona.models import Persona
from apps.empresa.models import Agencia
from apps.venta.models import Movimiento

#ventaPasaje|sobreCarga|encomiendaSalida|encomiendaLlegada|pagoProgramacion|pagoMensual->ingreso
#pagoPersonal|gastosAgencia -> egreso
class TipoMovimiento(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=[('ingreso','Ingreso'),('egreso','Egreso')])

    class Meta:

        verbose_name = 'TipoMovimiento'
        verbose_name_plural = 'TipoMovimientos'

    def __str__(self):
        return self.descripcion

#efectivo|yape|deposito,tranferencia
class TipoMedioPago(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion  = models.CharField(max_length=100)
    banco = models.CharField(max_length=50, blank=True,null=True)
    numCuenta = models.CharField(max_length=20, blank=True,null=True)
    numCci = models.CharField(max_length=20, blank=True,null=True)

    class Meta:
        verbose_name = 'TipoMedioPago'
        verbose_name_plural = 'TipoMedioPagos'

    def __str__(self):
       return self.nombre

class Caja(models.Model):
    nombreCaja = models.CharField(max_length=40)
    agencia = models.ForeignKey(Agencia, on_delete=models.PROTECT)
    montoEntrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montoSalida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    cajeros = models.ManyToManyField(Persona)

    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return self.nombreCaja


class MovimientoCaja(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT)
    cajero = models.ForeignKey(Persona, on_delete=models.PROTECT,related_name='cajero_movimientocaj', blank=True, null=True)
    numMov = models.IntegerField(blank=True, null=True)
    tipoMov = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    venta = models.OneToOneField(Movimiento, on_delete=models.PROTECT,blank=True, null=True)
    movFecha = models.DateField(verbose_name="Fecha del Comprobante",blank=True, null=True)    
    monto = models.DecimalField(max_digits=7, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    evidencia = models.ImageField(upload_to='media/egreso', blank=True, null=True)
    cliente = models.ForeignKey(Persona, on_delete=models.PROTECT, blank=True, null=True)
    

    class Meta:
        verbose_name = 'MovimientoCaja'
        verbose_name_plural = 'MovimientoCajas'

    def __str__(self):
        return str(self.id)

class MedioPago(models.Model):
    movimientoCaja = models.ForeignKey(MovimientoCaja, on_delete=models.PROTECT, blank=True,null=True)
    tipoMedioPago =  models.ForeignKey(TipoMedioPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=8,decimal_places=2,default=0)

    class Meta:
        verbose_name = 'MedioPago'
        verbose_name_plural = 'MedioPagos'

    def __str__(self):
         return str(self.monto)

class CierreCajaMes(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT)
    anio = models.SmallIntegerField()
    mes =  models.SmallIntegerField()
    totalEntrada = models.DecimalField(max_digits=10, decimal_places=2)
    totalSalida = models.DecimalField(max_digits=10, decimal_places=2)
    nombrePeriodo = models.CharField(max_length=20)
    movimientoCaja = models.ManyToManyField(MovimientoCaja)

    class Meta:
        verbose_name = 'CierreCajaMes'
        verbose_name_plural = 'CierreCajaMes'

    def __str__(self):
        return self.nombrePeriodo



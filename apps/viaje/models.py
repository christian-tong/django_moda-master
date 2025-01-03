from django.db import models
from django.forms import model_to_dict
from apps.venta.models import Movimiento
from apps.persona.models import Persona
from apps.empresa.models import Agencia,Vehiculo,Conductor,Asiento

class ProgramacionViaje(models.Model):
    nombreViaje = models.CharField(max_length=100, blank=True,null=True)
    rutaOrigen = models.ForeignKey(Agencia, on_delete=models.PROTECT)
    rutaDestino = models.ForeignKey(Agencia, on_delete=models.PROTECT, related_name='destino_viaje')
    fechaViaje = models.DateField()
    horaViaje = models.TimeField(default='12:00')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    piloto = models.ForeignKey(Conductor, on_delete=models.PROTECT, blank=True,null=True)
    copiloto = models.ForeignKey(Conductor, on_delete=models.PROTECT, blank=True,null=True, related_name='copiloto_viaje')
    ayudante = models.ForeignKey(Persona, on_delete=models.PROTECT, blank=True,null=True)
    terramosa = models.ForeignKey(Persona, on_delete=models.PROTECT, blank=True,null=True,related_name='terramosa_viaje')
    precio = models.DecimalField(max_digits=8, decimal_places=2, blank=True,null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'ProgramacionViaje'
        verbose_name_plural = 'ProgramacionViajes'

    def __str__(self):
        return self.nombreViaje
    
    def save(self, *args, **kwargs):
        self.nombreViaje = f'{self.rutaOrigen.nombre}-{self.rutaDestino.nombre}'
        return super(ProgramacionViaje, self).save(*args,**kwargs)

    def toJson(self):
        return model_to_dict(self)


Estado={
    ('vendido','Vendido'),
    ('libre','Libre'),
    ('reservado','Reservado'),
    ('cortesia','Cortesía'),
}
class ProgramacionAsiento(models.Model):
    programacionViaje = models.ForeignKey(ProgramacionViaje, on_delete=models.PROTECT,blank=True,null=True)
    asiento = models.ForeignKey(Asiento, on_delete=models.PROTECT,blank=True,null=True)    
    estado = models.CharField(max_length=30, choices=Estado,default='libre')
    precio = models.DecimalField(max_digits=7,decimal_places=2,blank=True,null=True)

    class Meta:

        verbose_name = 'ProgramacionAsiento'
        verbose_name_plural = 'ProgramacionAsientos'

    def __str__(self):
        return self.estado
    
    def toJson(self):
        return model_to_dict(self)


class Embarque(models.Model):
    numDocumento = models.CharField(max_length=8,blank=True,null=True)
    programacionViaje = models.ForeignKey(ProgramacionViaje, on_delete=models.PROTECT,blank=True,null=True)
    venta = models.OneToOneField(Movimiento, on_delete=models.PROTECT,blank=True,null=True)
    pasajero = models.ForeignKey(Persona, on_delete=models.PROTECT)
    lugar_abordo = models.ForeignKey(Agencia,verbose_name='Embarque', on_delete=models.PROTECT,blank=True,null=True)
    lugar_bajada = models.ForeignKey(Agencia,verbose_name='Desembarque', on_delete=models.PROTECT, related_name='embarque_bajada',blank=True,null=True)
    hora_abordo =  models.TimeField(default='12:00')
    observacion = models.TextField(verbose_name="Observaciones",blank=True,null=True)
    numAsiento = models.CharField(max_length=2)
    precio = models.DecimalField(max_digits=7,decimal_places=2,default=0)
    enSala = models.BooleanField(verbose_name='El pasajero esta en sala?',default=False)
    telefono = models.CharField(max_length=50,blank=True,null=True)
    escambio = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(Persona, on_delete=models.PROTECT ,related_name='embarque_usuario',blank=True,null=True)

    class Meta:
        verbose_name = 'Embarque'
        verbose_name_plural = 'Embarques'

    def __str__(self):
        return self.numDocumento

class Manifiesto(models.Model):
    numDocumento = models.CharField(max_length=8,blank=True,null=True)
    direccion = models.CharField(max_length=150,blank=True,null=True)
    fechaViaje = models.DateField(blank=True,null=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT,blank=True,null=True)
    piloto = models.ForeignKey(Conductor, on_delete=models.PROTECT, blank=True,null=True)
    copiloto = models.ForeignKey(Conductor, on_delete=models.PROTECT, blank=True,null=True, related_name='copiloto_manifiesto')
    programacionViaje = models.OneToOneField(ProgramacionViaje, on_delete=models.PROTECT, blank=True,null=True)    
    usuario = models.ForeignKey(Persona, on_delete=models.PROTECT,blank=True,null=True)
    modalidaServicio = models.CharField(max_length=30, default='Regular', blank=True,null=True)
    seGenero = models.BooleanField(default=False)
    embarque = models.ManyToManyField(Embarque, blank=True)
    printRutaOrigen = models.ForeignKey(Agencia, related_name='manifiesto_printrutaorigin', verbose_name='De', on_delete=models.PROTECT,blank=True,null=True)
    printRutaFinal = models.ManyToManyField(Agencia,through='ManifiestoRutaFinal', verbose_name='Destinos[*** Si va a guardar nuevos destinos, deseleccione todo y vuelva a seleccionar]',blank=True,null=True)    
    create = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    update = models.DateTimeField(auto_now=True,blank=True,null=True)

    class Meta:
        verbose_name = 'Manifiesto'
        verbose_name_plural = 'Manifiestos'

    def __str__(self):
        return self.numDocumento



class ManifiestoRutaFinal(models.Model):
    manifiesto = models.ForeignKey(Manifiesto, on_delete=models.CASCADE)
    agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE)
    orden = models.SmallIntegerField(null=True,blank=True)

    def __str__(self):
        return str(self.id)
import os
from datetime import datetime,date
from django.db import models
from django.forms import model_to_dict
from apps.catalogoSunat.models import TipoDocumentoIdentidad, Ubigeo



class Persona(models.Model):
    tipoDoc = models.ForeignKey(TipoDocumentoIdentidad,verbose_name='Tipo de Documento', on_delete=models.PROTECT)
    numDoc = models.CharField(verbose_name='Numero Documento', unique=True,max_length=11)
    denominacion = models.CharField(verbose_name='Razón Social/Nombre y Apellidos',max_length=150, blank=True, null=True)
    direccion = models.CharField(verbose_name='Dirección',max_length=255, blank=True, null=True)
    fijo = models.CharField(verbose_name='Teléfono fijo', blank=True, null=True,max_length=10)
    movilUno = models.PositiveIntegerField(verbose_name='Celular', blank=True, null=True)
    movilDos = models.PositiveIntegerField(verbose_name='Celular2', blank=True, null=True)
    correo = models.EmailField(verbose_name='Correo',max_length=250,blank=True, null=True)   
    ubigueo = models.ForeignKey(Ubigeo, on_delete=models.PROTECT, blank=True, null=True)
    activo = models.BooleanField(default=True)
    ispersonal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
       #return if self.denominacion not is None: self.denominacion; ""
       data = self.denominacion
       if data is None:
          data="-"
       return data
    
    def toJSON(self):
        item = model_to_dict(self,exclude=['foto',])
        item['tipoDoc'] = self.tipoDoc.toJSON()
        return item


GENERO=(
    ('F','Femenino'),
    ('M','Masculino'),
)

def rutaNombreImagen(instance, filename):
    extencion = os.path.splitext(filename)[1][1:]
    fecha = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    return f'persona/{instance.persona.numDoc}-{fecha}.' + extencion

class PersonaNatural(models.Model):
    persona = models.OneToOneField(Persona,on_delete=models.PROTECT,blank=True, null=True)
    nombres = models.CharField(max_length=100)
    apellidoP = models.CharField(max_length=100)
    apellidoM = models.CharField(max_length=100)
    fechaNac = models.DateField(verbose_name='Fecha de Nacimiento',blank=True, null=True)
    foto = models.ImageField(verbose_name='Foto',upload_to=rutaNombreImagen, default='persona/default.png',blank=True)
    genero = models.CharField(verbose_name='Género',max_length=10,choices=GENERO,blank=True, null=True)
    ordenhappy = models.SmallIntegerField(blank=True,null=True)

    class Meta:
        verbose_name = 'PersonaNatural'
        verbose_name_plural = 'PersonaNaturals'

    def __str__(self):
        return self.nombres

    def nombreCompleto(self):
        return f'{self.nombres}, {self.nombres} {self.nombres}'
    
    def saveOrdenCumpl(self):
        self.ordenhappy = self.fechaNac.strftime('%j')
        self.save(update_fields=['ordenhappy'])
        return self.ordenhappy

    def edad(self):
        try:
            edad = datetime.now().year - self.fechaNac.year
        except:
            edad = self.fechaNac
        
        return edad
    
    def happy(self):
        hoy = date.today()
        fecha_final = self.fechaNac
        try:            
            fecha = fecha_final.replace(year=hoy.year)            
            if hoy <= fecha:
                dif = fecha - hoy
                happy = dif.days
            else:
                fecha = fecha.replace(year=hoy.year + 1 )
                dif = fecha - hoy
                happy = dif.days
        except Exception as e:
            print(str(e))
            happy = 'No tiene FN'
        return happy
    
    
class PersonaJuridica(models.Model):
    persona = models.ForeignKey(Persona,on_delete=models.PROTECT)
    estado = models.BooleanField(default=True,blank=True, null=True)
    condicion = models.CharField(max_length=20,blank=True, null=True)

    class Meta:
        verbose_name = 'PersonaJuridica'
        verbose_name_plural = 'PersonaJuridicas'

    def __str__(self):
        return str(self.persona.id)


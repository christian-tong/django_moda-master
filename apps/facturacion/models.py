from urllib import request
from django.db import models
from apps.catalogoSunat.models import TipoDocumento
from apps.persona.models import Persona
from apps.venta.models import Movimiento
"""
class DocumentoOse(models.Model):
    pass
    venta = models.OneToOneField(Venta)
    operacion = models.CharField(max_length=11, default='generar_comprobante')
    tipo_de_comprobante = models.IntegerField(max_length=1)
    serie = models.CharField(max_length=4)
    numero = models.IntegerField(max_length=8)
    sunat_transaction = models.IntegerField(max_length=1)
    cliente_tipo_de_documento = models.CharField(max_length=1)
    cliente_numero_de_documento = models.CharField(max_length=15)
    cliente_denominacion = models.CharField(verbose_name='Razon Social/Nombre Completo',max_length=100)
    cliente_direccion = models.CharField(verbose_name='Direccion Completa|F~B',max_length=100)
    cliente_email = models.EmailField(max_length=250, blank=True,null=True)
    cliente_email_1 = models.EmailField(max_length=250, blank=True,null=True)
    cliente_email_2 = models.EmailField(max_length=250, blank=True,null=True)
    fecha_de_emision = models.DateField()
    fecha_de_vencimiento = models.DateField()
    moneda = models.IntegerField(max_length=1)
    tipo_de_cambio = models.DecimalField(max_digits=4,decimal_places=3, blank=True,null=True ) #condicional si ~PEN
    porcentaje_de_igv = models.DecimalField(max_digits=4,decimal_places=2, default=18.00)
    descuento_global = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_descuento = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_anticipo = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_gravada = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_inafecta = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_exonerada = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_igv = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_gratuita = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_otros_cargos = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_isc = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total = models.DecimalField(max_digits=14,decimal_places=2)
    percepcion_tipo = models.SmallIntegerField(max_length=1, blank=True,null=True)
    percepcion_base_imponible = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_percepcion = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_incluido_percepcion = models.DecimalField(max_digits=14,decimal_places=2,blank=True,null=True)
    retencion_tipo = models.SmallIntegerField(max_length=1,choices=[(1,'TASA 3%'),(2,'TASA 6%')], blank=True,null=True)
    retencion_base_imponible = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_retencion = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    total_impuestos_bolsas = models.DecimalField(max_digits=14,decimal_places=2, blank=True,null=True)
    detraccion = models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')], blank=True,null=True)
    observaciones = models.TextField(max_length=1000, blank=True,null=True)
    documento_que_se_modifica_tipo = models.SmallIntegerField(max_length=1, choices=[(1,'FACTURAS ELECTRÓNICA'),(2,'BOLETAS DE VENTA ELECTRÓNICAS')], blank=True,null=True)
    documento_que_se_modifica_serie = models.CharField(max_length=4,blank=True,null=True)
    documento_que_se_modifica_numero = models.IntegerField(max_length=8,blank=True,null=True)
    tipo_de_nota_de_credito = models.IntegerField(max_length=2,blank=True,null=True)
    tipo_de_nota_de_debito = models.IntegerField(max_length=2,blank=True,null=True)
    enviar_automaticamente_a_la_sunat =  models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')], blank=True,null=True)
    enviar_automaticamente_al_cliente =  models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')], blank=True,null=True)
    codigo_unico = models.CharField(max_length=20,blank=True,null=True)
    condiciones_de_pago = models.CharField(max_length=250,blank=True,null=True)
    medio_de_pago = models.CharField(max_length=250,blank=True,null=True)
    placa_vehiculo = models.CharField(max_length=8,blank=True,null=True)
    orden_compra_servicio  = models.CharField(max_length=20,blank=True,null=True)
    formato_de_pdf = models.CharField(max_length=6,choices=[('A4','A4'),('A5','A5'),('TICKET','TICKET')])
    generado_por_contingencia = models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')], blank=True,null=True)
    bienes_region_selva = models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')], blank=True,null=True)
    servicios_region_selva = models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')], blank=True,null=True)


    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return self.cliente_denominacion
    
class ItemOse(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.PROTECT)
    unidad_de_medida = models.CharField(max_length=5,choices=[('NIU','PRODUCTO'),('ZZ','SERVICIO')])
    codigo = models.CharField(max_length=250,blank=True,null=True)
    codigo_producto_sunat = models.CharField(max_length=8,blank=True,null=True)
    descripcion = models.TextField(max_length=250)
    cantidad = models.DecimalField(max_digits=14,decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=14,decimal_places=2) #sin igv | pre_uni/1.18
    precio_unitario = models.DecimalField(max_digits=14,decimal_places=2) #con igv | val_uni*1.18
    descuento = models.DecimalField(max_digits=14,decimal_places=2,blank=True,null=True) #desc antes de los impuestos
    subtotal = models.DecimalField(max_digits=14,decimal_places=2) #val_uni*cantidad-desc
    tipo_de_igv = models.SmallIntegerField(max_length=2)
    tipo_de_ivap = models.CharField(max_length=3,blank=True,null=True,choices=[('17','IVAP Gravado'),('101','IVAP Gratuito')])
    igv = models.DecimalField(max_digits=14,decimal_places=2) #Total igv de linea
    impuesto_bolsas = models.DecimalField(max_digits=14,decimal_places=2,blank=True,null=True,) 
    total = models.DecimalField(max_digits=14,decimal_places=2) 
    anticipo_regularizacion = models.CharField(max_length=5,choices=[('false','FALSO'),('true','VERDADERO')])
    anticipo_documento_serie = models.CharField(max_length=4,blank=True,null=True)
    anticipo_documento_numero = models.IntegerField(max_length=8,blank=True,null=True)
    tipo_de_isc = models.DecimalField(max_digits=14,decimal_places=2,blank=True,null=True,) 
    isc = models.DecimalField(max_digits=14,decimal_places=2,blank=True,null=True,) 

    class Meta:

        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.descripcion


class VentaCreditoOse(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.PROTECT)
    cuota = models.SmallIntegerField(max_length=3)
    fecha_de_pago = models.DateField()
    importe = models.DecimalField(max_digits=14,decimal_places=2)

    class Meta:

        verbose_name = 'VentaCredito'
        verbose_name_plural = 'VentaCreditos'

    def __str__(self):
        return str(self.importe)

class GuiaOse(models.Model):

    documento = models.ForeignKey(Documento, on_delete=models.PROTECT)
    guia_tipo = models.SmallIntegerField(max_length=1,choices=[(1,'GUÍA DE REMISIÓN REMITENTE'),(2,'GUÍA DE REMISIÓN TRANSPORTISTA')])
    guia_serie_numero = models.CharField(max_length=30)#serie-numero numeros propios


    class Meta:

        verbose_name = 'Guia'
        verbose_name_plural = 'Guias'

    def __str__(self):
        return self.guia_tipo

"""

"""class FacturaBoleta(models.Model):
    vendedor = models.ForeignKey(Persona, on_delete=models.PROTECT)
    venta = models.OneToOneField(Venta)    
    tipoComprobante = models.CharField(max_length=2)
    serieComprobante = models.CharField(max_length=4)
    numComprobante = models.IntegerField(max_length=8)
    tipOperacion = models.ForeignKey(TipoOperacion, on_delete=models.PROTECT)#catalogo51
    fecEmision = models.DateField(auto_now=True)
    horEmision = models.TimeField(auto_now=True)
    fecVencimiento =  models.DateField(null=True,blank=True)    
    tipMoneda = models.ForeignKey(TipoMonedaIso, on_delete=models.PROTECT) # catalogo 2
    cliente = models.ForeignKey(Persona, on_delete=models.PROTECT) #11 12 13
    totalGravadas
    totalInafectas
    totalExoneradas
    totalGratuitas
    sumIgv
    totalTributos
    totaValorVenta
    subTotalFactura
    importeTotalVenta
    leyenda = models.ForeignKey(Leyenda, on_delete=models.PROTECT)



    class Meta:

        verbose_name = 'FacturaBoleta'
        verbose_name_plural = 'FacturaBoletas'

    def __str__(self):

class FacturaBoletaItem(models.Model):
    unidadMedida
    cantidad
    descripcion
    valorUnitario
    precioUnitario
    afectacionIgv  #catalogo 07
    porcentajeDescuento
    montoDescuento
    valorVenta
    totalTributos

    class Meta:
        verbose_name = 'FacturaBoletaItem'
        verbose_name_plural = 'FacturaBoletaItems'

    def __str__(self):
"""

#documento
class FaturaBoleta(models.Model):
    ventaMovimiento = models.OneToOneField(Movimiento, on_delete=models.PROTECT,blank=True,null=True)
    tipoDocumento = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    serie = models.CharField(max_length=4,blank=True,null=True)
    numero = models.IntegerField(blank=True,null=True)
    cliente = models.ForeignKey(Persona, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Persona, on_delete=models.PROTECT,related_name='usuario_factura', blank=True,null=True)
    monto = models.DecimalField(max_digits=8,decimal_places=2 ,default=0,blank=True,null=True)
    fechaFact = models.DateField(auto_now=True)
    estaFacturado = models.BooleanField(blank=True,null=True)
    iscanje = models.BooleanField(blank=True,null=False)
    enlace = models.URLField(blank=True,null=False)
    cadenaqr = models.CharField(max_length=255, blank=True,null=False)
    hora = models.TimeField(auto_now=True)
    

    class Meta:
        verbose_name = 'FaturaBoleta'
        verbose_name_plural = 'FaturaBoletas'

    def __str__(self):
        return str(self.id)
    

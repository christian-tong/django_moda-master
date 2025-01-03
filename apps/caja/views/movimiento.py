from django.shortcuts import redirect, render
from django.forms import formset_factory
from django.contrib import messages
from urllib.parse import urlencode
from django.urls import reverse
from django.db import transaction
from apps.caja.forms import BaseMedioPagoFormSet,MedioPagoForm
from apps.catalogoSunat.models import TipoDocumento
from apps.facturacion.forms import FacturaBoletaForm
from apps.venta.models import Movimiento
from apps.empresa.models import AgenciaDocumento
from ..models import Caja, MovimientoCaja,TipoMovimiento
from desatendidos.correlativoDoc import incrementa

       
def movimiento_add(request):
    idmov = int(request.GET.get('mov'))
    tipomovi = request.GET.get('tipomov')
    
    venta = Movimiento.objects.get(id=idmov)
    montoCobrar=0.0

    if tipomovi == 'ventaPasaje':
        montoCobrar = venta.embarque.precio      
        detalle = f'Venta de pasaje, ruta: {venta.embarque.programacionViaje.nombreViaje}'
        factura_cliente = venta.embarque.pasajero
    elif tipomovi=='encomiendaSalida' or tipomovi=='encomiendaLlegada':
        montoCobrar = venta.encomienda.precio
        detalle = f'Servicio de encomienda, ruta: {venta.encomienda.agenciaOrigen.nombre} - {venta.encomienda.agenciaDestino.nombre}'
        factura_cliente = venta.encomienda.remite
    else:
        return ''
    tipdoc = TipoDocumento.objects.filter(codigo='03').first()
    if request.method == 'GET':
        factura = FacturaBoletaForm(initial={'tipoDocumento':tipdoc,}, cliente=factura_cliente)

    MedioPagoFormSet = formset_factory(MedioPagoForm,formset=BaseMedioPagoFormSet,  extra = 0)
    formset = MedioPagoFormSet(initial=[{'tipoMedioPago':1,'monto':montoCobrar},])

    if request.method == 'POST':
        try:
            with transaction.atomic():
                #¡¡¡¡ Alerta luego ver si tiene configurado, documentos(Boleta,Factura,Caja)
                factura = FacturaBoletaForm(request.POST)
                formset = MedioPagoFormSet(request.POST)

                if factura.is_valid() and formset.is_valid():                  

                    caja = Caja.objects.get(agencia=request.user.agencia.get(id=request.session['agencia_id']))
                    docum = incrementa(request,'CA')
                    movCaja = MovimientoCaja(
                                caja = caja,
                                numMov = docum['correlativo'],
                                tipoMov = TipoMovimiento.objects.get(nombre=tipomovi),
                                venta = venta,
                                monto = montoCobrar,
                                descripcion = detalle,
                                cliente = factura.cleaned_data['cliente'],
                                cajero = request.user.persona

                    )
                    
                    movCaja.save()
                    
                    for form in formset:
                        instance = form.save(commit=False)
                        instance.movimientoCaja=movCaja
                        instance.save()

                    # guardar en db facturacion
                    fac = factura.save(commit=False)
                    fac.ventaMovimiento = venta
                    fac.serie = docum['serie']
                    fac.numero = docum['correlativo']
                    fac.monto = montoCobrar
                    fac.estaFacturado = False
                    fac.usuario = request.user.persona
                    fac.save()
                    
                    messages.success(request,'Pago registrado con exito..')
                    #return redirect('web:index-sistema')
                    idmov =idmov
                    parametro={'fromCityName':'chintucaycuri%20%28Todos%29&fromCityId=195648','tipomovi':tipomovi,'toCityName':'Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER','mov':idmov,'destCountry':'PER&opId=0&busType=Any'}
                    return redirect(f"{reverse('facturacion:boleta-print')}?{urlencode(parametro)}")
        except Exception as e:
            print(e)
            messages.error(request,f"Algo salio mal al momento de guardar los datos(Error: {e}")

    context={
        'factura': factura,
        'medioPagos': formset,
        'montoCobrar':montoCobrar
    }

    return render(request,'apps/caja/movimiento/add.html',context)

import io
import qrcode
import qrcode.image.svg
from desatendidos.exportFile import FormatoExcel
from desatendidos.numeroLetras import numero_to_letras
from desatendidos.envioOse import logicaEnvioOse
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.empresa.models import Agencia
from apps.facturacion.forms import FacturaBoletaForm
from apps.venta.models import Movimiento
from .models import FaturaBoleta

from django.conf import settings


def list(request):
    q = request.GET.get("q", "")
    page = request.GET.get("page", 1)
    add_ruta_get = ""
    data = FaturaBoleta.objects.all().order_by("-fechaFact")

    if q:
        print(q)
        print(type(q))
        data = (
            FaturaBoleta.objects.filter(
                Q(cliente__denominacion__icontains=q) | Q(cliente__numDoc__icontains=q)
            )
            .order_by("-fechaFact")
            .distinct()
        )
        add_ruta_get = f"&q={q}"

    # paginator
    if data:
        try:
            paginator = Paginator(data, settings.NUM_PAGINATE)
            data = paginator.page(page)
        except:
            # raise Http404
            data = {}
            messages.info(request, "Se excedió en paginas")
    else:
        messages.info(request, "No tiene registro con los parametros ")
        paginator = ""

    context = {
        "entity": data,
        "paginator": paginator,
        "add_ruta_get": add_ruta_get,
        "q": q,
    }
    return render(request, "apps/facturacion/list.html", context)


def enviarOse(request, pk):
    fact = FacturaBoletaForm()
    movimiento = get_object_or_404(Movimiento, pk=pk)
    montoCobrar = movimiento.faturaboleta.monto
    factura = movimiento.faturaboleta
    if not factura.estaFacturado:
        if request.method == "POST":
            fact = FacturaBoletaForm(request.POST)
            if fact.is_valid():
                factura.tipoDocumento = fact.cleaned_data["tipoDocumento"]
                factura.cliente = fact.cleaned_data["cliente"]
                factura.save()
                req = logicaEnvioOse(pk, factura, True)
                if req.get("errors"):
                    messages.info(request, f"Hay un error de la ose, {req['errors']}")
                else:
                    messages.info(request, "El documento fue creado exitosamente")
                return redirect("facturacion:list")
    else:
        messages.info(request, "El documento ya fue facturado")
        return redirect("facturacion:list")
    context = {"factura": fact, "montoCobrar": montoCobrar}
    return render(request, "apps/facturacion/enviar-ose.html", context)


def boletaPrint(request):
    mov_id = request.GET.get("mov")
    tipomovi = request.GET.get("tipomovi")

    movimiento = get_object_or_404(Movimiento, pk=mov_id)
    principal = Agencia.objects.filter(tipo="PRINCIPAL")[0]
    idencomienda = None

    # -------API NUBEFACT---------
    ####validar si es factura o boleta, si es ticke no enviar a la ose
    factura = movimiento.faturaboleta
    image_qr = None

    if not factura.estaFacturado:
        req = logicaEnvioOse(mov_id, factura, False)
        if req.get("errors"):
            # return JsonResponse({'data':f"Error de ose {req['errors']}"}, safe = False)
            messages.error(
                request,
                f"No se ah podido facturar, le enviaremos mas tarde a su correo o a su whatsapp <br> {req['errors']}",
            )
            image_qr = None
        else:
            messages.success(request, "La facturación fue exitosa")
            data = req["cadena_para_codigo_qr"]
            # ---------------qr------------
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(data, image_factory=factory, box_size=6)
            stream = io.BytesIO()
            img.save(stream)
            image_qr = stream.getvalue().decode()
            # ------------------fin-------
    if tipomovi == "ventaPasaje":
        totales = movimiento.embarque.precio
    else:
        totales = movimiento.encomienda.precio
        idencomienda = movimiento.encomienda.id
    context = {
        "tipomovi": tipomovi,
        "movimiento": movimiento,
        "image_qr": image_qr,
        "num_letras": numero_to_letras(totales),
        "totales": totales,
        "principal": principal,
        "idencomienda": idencomienda,
    }
    return render(request, "apps/facturacion/print-caja.html", context)


def detallePrint(request):
    mov_id = request.GET.get("mov")
    tipomovi = request.GET.get("tipomovi")

    movimiento = get_object_or_404(Movimiento, pk=mov_id)
    principal = Agencia.objects.filter(tipo="PRINCIPAL")[0]

    factura = movimiento.faturaboleta
    image_qr = None
    idencomienda = None

    if factura.estaFacturado:
        data = factura.cadenaqr
        # ---------------qr------------
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(data, image_factory=factory, box_size=6)
        stream = io.BytesIO()
        img.save(stream)
        image_qr = stream.getvalue().decode()
        # ------------------fin-------
    if tipomovi == "ventaPasaje":
        totales = movimiento.embarque.precio
    else:
        totales = movimiento.encomienda.precio
        idencomienda = movimiento.encomienda.id

    context = {
        "tipomovi": tipomovi,
        "movimiento": movimiento,
        "image_qr": image_qr,
        "num_letras": numero_to_letras(totales),
        "totales": totales,
        "principal": principal,
        "idencomienda": idencomienda,
    }
    return render(request, "apps/facturacion/print-caja.html", context)


def ComprobanteExcel(request):
    periodo = request.GET.get("periodo")
    # 2022-07
    year = int(periodo[:4])
    mes = int(periodo[5:])

    name_doc = "export-comprobantes"
    name_sheet = f"documento-{periodo}"
    columns = [
        "Tipo Comprobante",
        "Serie",
        "Numero",
        "Cliente",
        "Tipo Documento",
        "Numero",
        "Monto",
        "Fecha",
        "Detalle",
    ]
    obj = FaturaBoleta.objects.filter(
        fechaFact__year=year, fechaFact__month=mes, estaFacturado=True
    ).values_list(
        "tipoDocumento__descripcion",
        "serie",
        "numero",
        "cliente__denominacion",
        "cliente__tipoDoc__descripcion",
        "cliente__numDoc",
        "monto",
        "fechaFact",
        "ventaMovimiento__detallemov__descripcion",
    )

    return FormatoExcel(columns, obj, name_doc, name_sheet)

from io import BytesIO

from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Sum
from urllib.parse import urlencode
from apps.empresa.models import AgenciaDocumento
from apps.venta.forms import DetalleMovForm
from apps.venta.models import Movimiento
from .models import Encomienda, Liquidacion
from .forms import (
    EncomiendaForm,
    LiquidacionForm,
    liquidacionRecepcionForm,
    ClienteRecepcionForm,
)
from desatendidos.correlativoDoc import incrementa
from desatendidos.htmlPdf import render_to_pdf


def encomiendaList(request):
    page = request.GET.get("page", 1)
    q = request.GET.get("q", "")
    add_ruta_get = ""

    if q:
        data = (
            Encomienda.objects.filter(
                Q(consignado__numDoc__icontains=q)
                | Q(consignado__denominacion__icontains=q)
            )
            .order_by("-venta__create")
            .distinct()
        )
        add_ruta_get = f"&q={q}"
    else:
        data = Encomienda.objects.all().order_by("-venta__create")

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

    return render(request, "apps/envio/encomienda/list.html", context)


def encomiendaAdd(request):
    numEncomienda = AgenciaDocumento.objects.get(
        agencia=request.user.agencia.get(id=request.session["agencia_id"]),
        documento__codigo="EN",
    )
    form = EncomiendaForm()
    detalle = DetalleMovForm()

    if request.method == "POST":
        form = EncomiendaForm(request.POST)
        detalle = DetalleMovForm(request.POST)

        if detalle.is_valid():
            venta = Movimiento(
                vendedor=request.user.persona,
                agencia=request.user.agencia.get(id=request.session["agencia_id"]),
            )
            venta.save()

            detencomienda = detalle.save(commit=False)
            detencomienda.movimiento = venta
            detencomienda.subTotal = (
                detencomienda.cantidad * detencomienda.valorUnitario
            )
            detencomienda.save()

            correlativoAgeUpd = AgenciaDocumento.objects.get(
                agencia=request.user.agencia.get(id=request.session["agencia_id"]),
                documento__codigo="EN",
            )

            encomienda = dict(
                numDocumento=correlativoAgeUpd.correlativoMas(),
                venta=venta,
                remite_id=request.POST["remite"],
                consignado_id=request.POST["consignado"],
                agenciaOrigen_id=request.POST["agenciaOrigen"],
                agenciaDestino_id=request.POST["agenciaDestino"],
                esContraEntrega=True
                if request.POST.get("esContraEntrega", False) == "on"
                else False,
                aDomicilio=True
                if request.POST.get("aDomicilio", False) == "on"
                else False,
                domicilio=request.POST["domicilio"],
                seguridadClave=request.POST["seguridadClave"],
                observacion=request.POST["observacion"],
                estado="agenciaOrigen",
                precio=detalle.cleaned_data["cantidad"]
                * detalle.cleaned_data["valorUnitario"],
                numeroContacto=request.POST["numeroContacto"],
            )

            encomienda = Encomienda.objects.create(**encomienda)
            messages.success(request, "Encomienda registrado con exito..")

            if encomienda.esContraEntrega:
                idencom = encomienda.id
                parametro = {
                    "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                    "tipomov": "encomiendaSalida",
                    "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                    "encom_pk": idencom,
                    "destCountry": "PER&opId=0&busType=Any",
                }
                return redirect(
                    f"{reverse('envio:encomienda-print')}?{urlencode(parametro)}"
                )

            else:
                idmov = venta.id
                parametro = {
                    "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                    "tipomov": "encomiendaSalida",
                    "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                    "mov": idmov,
                    "destCountry": "PER&opId=0&busType=Any",
                }
                return redirect(
                    f"{reverse('tesoreria:tesoreria-movimiento-add')}?{urlencode(parametro)}"
                )

    context = {
        "form": form,
        "detalle": detalle,
        "numEncomienda": numEncomienda.correlativo,
    }

    return render(request, "apps/envio/encomienda/add.html", context)


def encomiendaRecepcion(request):
    encomienda_pk = request.GET.get("encom_pk")
    encomienda = get_object_or_404(Encomienda, pk=encomienda_pk)
    form_clie_recp = ClienteRecepcionForm

    if request.method == "POST":
        form_clie_recp = ClienteRecepcionForm(request.POST, request.FILES)
        if form_clie_recp.is_valid():
            if encomienda.seguridadClave != form_clie_recp.cleaned_data.get("clave"):
                messages.error(request, "Clave incorrecta..")
            else:
                form = form_clie_recp.save(commit=False)
                form.encomienda = encomienda
                form.usuario = request.user.persona
                form.save()

                encomienda.estado = "recepcionado"
                encomienda.save()
                messages.success(request, "Se entrego con exito..")

                if encomienda.esContraEntrega:
                    idmov = encomienda.venta.id
                    parametro = {
                        "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                        "tipomov": "encomiendaLlegada",
                        "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                        "mov": idmov,
                        "destCountry": "PER&opId=0&busType=Any",
                    }
                    return redirect(
                        f"{reverse('tesoreria:movimiento-add')}?{urlencode(parametro)}"
                    )

    context = {"encomienda": encomienda, "form_clie_recp": form_clie_recp}

    return render(request, "apps/envio/encomienda/recepcion.html", context)


def encomiendaPrint122(request):
    encom_pk = request.GET.get("encom_pk")
    encomienda = get_object_or_404(Encomienda, pk=encom_pk)

    # Indicamos el tipo de contenido a devolver, en este caso un pdf
    response = HttpResponse(content_type="application/pdf")
    # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
    buffer = BytesIO()
    # Canvas nos permite hacer el reporte con coordenadas X y Y
    pdf = canvas.Canvas(buffer, pagesize=A4)

    encabezado(pdf, encomienda)

    pdf.line(180, 570, 460, 570)
    pdf.drawString(200, 558, "DETALLE DEL SERVICIO")
    pdf.drawString(330, 558, "CANT")
    pdf.drawString(380, 558, "TARF")
    pdf.drawString(430, 558, "SUBT")
    pdf.line(180, 555, 460, 555)
    for item in encomienda.venta.detallemov_set.all():
        pdf.drawString(200, 546, item.descripcion)
        pdf.drawString(330, 546, f"{item.cantidad}")
        pdf.drawString(380, 546, f"{item.valorUnitario}")
        pdf.drawString(430, 546, f"{item.subTotal}")

    pdf.drawString(330, 526, "IMPORTE A PAGAR")
    pdf.drawString(430, 526, f"{item.subTotal}")

    pdf.showPage()
    pdf.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def encomiendaPrint453(request):
    encom_pk = request.GET.get("encom_pk")
    encomienda = get_object_or_404(Encomienda, pk=encom_pk)

    response = HttpResponse(content_type="application/pdf")
    # response['Content-Disposition']='attachment;filename=hohoh.pdf'
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    # c.setPageSize((58, 210))
    encabezado(c, encomienda)
    # table header
    styles = getSampleStyleSheet()
    styleBH = styles["Normal"]
    styleBH.alignment = TA_CENTER
    styleBH.fontSize = 8

    a = Paragraph("DETALLE DEL SERVICIO", styleBH)
    b = Paragraph("CANT", styleBH)
    cc = Paragraph("TARF", styleBH)
    d = Paragraph("SUBT", styleBH)

    data = []
    data.append([a, b, cc, d])

    # Table
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 10

    high = 520
    for item in encomienda.venta.detallemov_set.all():
        enco = [
            Paragraph(item.descripcion, styleN),
            item.cantidad,
            item.valorUnitario,
            item.subTotal,
        ]
        data.append(enco)
        high = high - 18

    data.append(["Total a Pagar", "", "", item.subTotal])

    # table size
    width, height = A4
    table = Table(data, colWidths=[4 * cm, 2 * cm, 2 * cm, 2 * cm])
    table.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )

    # pdf size
    table.wrapOn(c, width, height)
    table.drawOn(c, 180, high)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(250, high - 30, "Gracias por su preferencia")

    c.setFont("Helvetica", 10)
    c.drawString(200, high - 50, "Registrado por:")
    c.drawString(300, high - 50, f": {encomienda.venta.vendedor}")

    c.showPage()

    # save pdf
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def encabezado(pdf, encomienda):
    pdf.setDash(1, 2)
    pdf.setFont("Helvetica", 30)
    pdf.drawString(285, 770, "Logo")
    pdf.setFont("Helvetica", 10)
    emp = (len("MODA TOURS S.A.C") * 7) / 2
    pdf.drawString(320 - emp, 730, "MODA TOURS S.A.C")

    dire = (len("DIRECCION EMPRESA") * 7) / 2
    pdf.drawString(320 - dire, 716, "DIRECCION EMPRESA")

    ubigeo = (len("PROVINCIA-DEPARTAMENTO-DISTRITO") * 7) / 2
    pdf.drawString(320 - ubigeo, 702, "PROVINCIA-DEPARTAMENTO-DISTRITO")

    tlf = (len("TELEFONO:9999966") * 7) / 2
    pdf.drawString(320 - tlf, 688, "TELEFONO:9999966")

    ruc = (len("RUC:246666512547") * 7) / 2
    pdf.drawString(320 - ruc, 674, "RUC:20393819660")

    pdf.setFont("Helvetica-Bold", 12)
    doc = (len("TICKET DE ENVIO") * 7) / 2
    pdf.drawString(310 - doc, 660, "TICKET DE ENVIO")

    pdf.setFillColorRGB(255, 0, 0)
    pdf.setFont("Helvetica", 12)
    numdoc = (len("N° - 000545") * 7) / 2
    pdf.drawString(310 - numdoc, 646, f"N° - 000{encomienda.numDocumento}")

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 9)
    pdf.line(180, 640, 460, 640)

    pdf.drawString(200, 625, "ORIGEN")
    pdf.drawString(300, 625, f": {encomienda.agenciaOrigen}")

    pdf.drawString(200, 613, "DESTINO")
    pdf.drawString(300, 613, f": {encomienda.agenciaDestino}")

    pdf.drawString(200, 601, "REMITENTE")
    pdf.drawString(300, 601, f": {encomienda.remite}")

    pdf.drawString(200, 589, "CONSIGNADO")
    pdf.drawString(300, 589, f": {encomienda.consignado}")

    pdf.drawString(200, 577, "FORMA DE PAGO")
    if encomienda.esContraEntrega:
        pdf.drawString(300, 577, ": Contra Entrega")
    else:
        pdf.drawString(300, 577, ": Contado")

    pdf.drawString(200, 565, "FECHA")
    pdf.drawString(300, 565, f": {encomienda.venta.create}")


def encomiendaPrint(request):
    encom_pk = request.GET.get("encom_pk")
    encomienda = get_object_or_404(Encomienda, pk=encom_pk)
    total = encomienda.venta.detallemov_set.all().aggregate(Sum("subTotal"))[
        "subTotal__sum"
    ]

    context = {"encomienda": encomienda, "total": total}
    return render(request, "apps/envio/encomienda/print.html", context)


def liquidacionList(request):
    page = request.GET.get("page", 1)
    q = request.GET.get("q", "")
    add_ruta_get = ""

    data = Liquidacion.objects.all().order_by("-fecha")

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

    return render(request, "apps/envio/liquidacion/list.html", context)


def liquidacionAdd(request):
    liquidacion = LiquidacionForm()
    correlativoAgeUpd = AgenciaDocumento.objects.get(
        agencia=request.user.agencia.get(id=request.session["agencia_id"]),
        documento__codigo="LI",
    )

    if request.method == "POST":
        liquidacion = LiquidacionForm(request.POST)
        if liquidacion.is_valid():
            liq = liquidacion.save(commit=False)
            liq.numDocumento = incrementa(request, "LI")["correlativo"]
            liq.usuario = request.user.persona
            liq.save()

            id_liq = liq.id
            parametro = {
                "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                "tipomov": "encomiendaSalida",
                "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                "li_pk": id_liq,
                "destCountry": "PER&opId=0&busType=Any",
            }
            return redirect(
                f"{reverse('envio:liquidacion-add-encomienda')}?{urlencode(parametro)}"
            )

    context = {"liquidacion": liquidacion, "correlativo": correlativoAgeUpd.correlativo}

    return render(request, "apps/envio/liquidacion/add.html", context)


def liquidacionEdit(request):
    liquidacion_pk = request.GET.get("li_pk")
    data = get_object_or_404(Liquidacion, pk=liquidacion_pk)

    form_liquidacion = LiquidacionForm(instance=data)
    encomienda = data.encomienda.all()
    liquidacion_recp = ""
    if data.finalizado:
        liquidacion_recp = data.usuario

    else:
        if request.method == "POST":
            form_liquidacion = LiquidacionForm(request.POST, instance=data)

            if form_liquidacion.is_valid():
                p = form_liquidacion.save(commit=False)
                p.save(
                    update_fields=[
                        "agenciaOrigen",
                        "agenciaDestino",
                        "vehiculo",
                        "conductor",
                    ]
                )
                return redirect("envio:liquidacion-list")

    context = {
        "liquidacion": form_liquidacion,
        "entity": encomienda,
        "liquidacion_pk": liquidacion_pk,
        "liquidacion_recp": liquidacion_recp,
    }
    return render(request, "apps/envio/liquidacion/edit.html", context)


def liquidacionAddEncomienda(request):
    liquidacion_pk = request.GET.get("li_pk")
    liquidacion = get_object_or_404(Liquidacion, pk=liquidacion_pk)
    encomienda = Encomienda.objects.filter(
        agenciaOrigen=liquidacion.agenciaOrigen, estado="agenciaOrigen"
    ).exclude(pk__in=liquidacion.encomienda.all().values("id"))

    if request.method == "POST":
        encom = request.POST.getlist("_selected_action")
        liquidacion.encomienda.add(*encom)
        parametro = {
            "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
            "tipomovi": "tipomovi",
            "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
            "li_pk": liquidacion_pk,
            "destCountry": "PER&opId=0&busType=Any",
        }
        return redirect(f"{reverse('envio:liquidacion-edit')}?{urlencode(parametro)}")

    context = {"entity": encomienda, "liquidacion_pk": liquidacion_pk}

    return render(request, "apps/envio/liquidacion/add-encomienda.html", context)


def liquidacionSacarEncomienda(request):
    liquidacion_pk = request.GET.get("li_pk")
    liquidacion = get_object_or_404(Liquidacion, pk=liquidacion_pk)

    if request.method == "POST":
        encom = request.POST.getlist("_selected_action")
        liquidacion.encomienda.remove(*encom)
        parametro = {
            "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
            "tipomovi": "tipomovi",
            "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
            "li_pk": liquidacion_pk,
            "destCountry": "PER&opId=0&busType=Any",
        }
        return redirect(f"{reverse('envio:liquidacion-edit')}?{urlencode(parametro)}")

    return render(request, "apps/envio/liquidacion/add-encomienda.html", context={})


def liquidacionFinalizar(request):
    liquidacion_pk = request.GET.get("li_pk")
    liquidacion = get_object_or_404(Liquidacion, pk=liquidacion_pk)

    if request.method == "POST":
        liquidacion.finalizado = True
        liquidacion.usuario = request.user.persona
        liquidacion.save()

        liquidacion.encomienda.all().update(estado="enCamino")

        return redirect("envio:liquidacion-list")

    context = {"liquidacion": liquidacion, "liquidacion_pk": liquidacion_pk}

    return render(request, "apps/envio/liquidacion/finalizar.html", context)


def liquidacionRecepcion(request):
    liquidacion_pk = request.GET.get("li_pk")
    liquidacion = get_object_or_404(Liquidacion, pk=liquidacion_pk)
    encomienda = liquidacion.encomienda.all()

    liquidacion_recp = ""

    try:
        form_liq_recep = liquidacionRecepcionForm(
            instance=liquidacion.liquidacionrecepcion
        )
        liquidacion_recp = liquidacion.liquidacionrecepcion.usuario

    except:
        form_liq_recep = liquidacionRecepcionForm
        if request.method == "POST":
            form_liq_recep = liquidacionRecepcionForm(request.POST)
            if form_liq_recep.is_valid():
                formlr = form_liq_recep.save(commit=False)
                formlr.usuario = request.user.persona
                formlr.liquidacion = liquidacion
                formlr.save()
                liquidacion.encomienda.all().update(estado="agenciaDestino")

                return redirect("envio:liquidacion-list")

    context = {
        "liquidacion": liquidacion,
        "entity": encomienda,
        "liquidacion_recp": liquidacion_recp,
        "form_liq_recep": form_liq_recep,
    }
    return render(request, "apps/envio/liquidacion/recepcion.html", context)


def liquidacionPrint(request):
    liquidacion_pk = request.GET.get("li_pk")
    liquidacion = get_object_or_404(Liquidacion, pk=liquidacion_pk)
    encomiendas = liquidacion.encomienda.all().order_by(
        "-agenciaDestino", "esContraEntrega"
    )
    suma_directa = liquidacion.encomienda.filter(esContraEntrega=False).aggregate(
        Sum("precio")
    )["precio__sum"]
    suma_contra_entrega = liquidacion.encomienda.filter(esContraEntrega=True).aggregate(
        Sum("precio")
    )["precio__sum"]
    if suma_directa is None:
        suma_directa = 0
    if suma_contra_entrega is None:
        suma_contra_entrega = 0

    suma_total = suma_directa + suma_contra_entrega
    comision_chofer = suma_total * 60 / 100
    comision_agencia = suma_total * 40 / 100

    context = {
        "liquidacion": liquidacion,
        "encomiendas": encomiendas,
        "suma_directa": suma_directa,
        "suma_contra_entrega": suma_contra_entrega,
        "suma_total": suma_total,
        "comision_chofer": comision_chofer,
        "comision_agencia": comision_agencia,
    }

    pdf = render_to_pdf("apps/envio/liquidacion/print.html", context)
    return HttpResponse(pdf, content_type="application/pdf")


def encomiendaPrintA5(request, encom_pk):
    encomienda = get_object_or_404(Encomienda, pk=encom_pk)
    total = encomienda.venta.detallemov_set.all().aggregate(Sum("subTotal"))[
        "subTotal__sum"
    ]

    context = {"encomienda": encomienda, "total": total}

    pdf = render_to_pdf("apps/envio/encomienda/printa5.html", context)
    return HttpResponse(pdf, content_type="application/pdf")

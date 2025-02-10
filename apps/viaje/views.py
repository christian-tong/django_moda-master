import math
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse

from urllib.parse import urlencode
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from apps.venta.models import Movimiento, DetalleMov
from .models import (
    Embarque,
    Manifiesto,
    ProgramacionAsiento,
    ProgramacionViaje,
)
from .forms import (
    EmbarqueForm,
    ProgramacionViajeForm,
    BuscarViajeForm,
    ManifiestoForm,
    EmbarqueEditForm,
    ProgramacionAsientoForm,
)
from django.db.models import Q
from desatendidos.correlativoDoc import incrementa
from desatendidos.htmlPdf import render_to_pdf


def embarqueList(request):
    search = request.GET.get("q", "")
    add_ruta_get = ""
    page = request.GET.get("page", 1)
    pasajeros = Embarque.objects.all().order_by("-create")

    if search:
        add_ruta_get = f"&q={search}"
        pasajeros = (
            Embarque.objects.filter(
                Q(pasajero__denominacion__icontains=search)
                | Q(pasajero__numDoc__icontains=search)
            )
            .order_by("-create")
            .distinct()
        )

    # paginacion
    if pasajeros:
        try:
            paginator = Paginator(pasajeros, settings.NUM_PAGINATE)
            pasajeros = paginator.page(page)
        except:
            # raise Http404
            pasajeros = {}
            messages.info(request, "Se excedió en paginas")
    else:
        messages.info(request, "No tiene registro con los parametros ")
        paginator = ""

    context = {
        "entity": pasajeros,
        "q": search,
        "paginator": paginator,
        "add_ruta_get": add_ruta_get,
    }

    return render(request, "apps/viaje/embarque/list.html", context)


def embarqueAdd(request):
    embarque = {}
    viajeProgramado = {}
    asientoProgramado = {}
    idPrograma = request.POST.get("id_programa", False)

    if idPrograma:
        viajeProgramado = ProgramacionViaje.objects.get(id=idPrograma)
        asientoProgramado = ProgramacionAsiento.objects.filter(
            programacionViaje=viajeProgramado
        ).order_by("asiento__codigoMatrix")
        embarque = EmbarqueForm(
            initial={
                "lugar_abordo": viajeProgramado.rutaOrigen,
                "lugar_bajada": viajeProgramado.rutaDestino,
                "hora_abordo": viajeProgramado.horaViaje.isoformat()[:5],
            }
        )

    else:
        if request.method == "POST":
            idPrograma = int(request.POST.get("idprograma"))
            viajeProgramado = ProgramacionViaje.objects.get(id=idPrograma)
            asientoProgramado = ProgramacionAsiento.objects.filter(
                programacionViaje=viajeProgramado
            ).order_by("asiento__codigoMatrix")

            # Venta
            venta = Movimiento(
                vendedor=request.user.persona,
                agencia=request.user.agencia.get(id=request.session["agencia_id"]),
            )
            venta.save()

            # Detalle venta
            detalle = DetalleMov(
                movimiento=venta,
                descripcion=f"SERVICIO DE TRANSPORTE EN LA RUTA ({request.POST['lugar_abordo']} - {request.POST['lugar_bajada']})",
                valorUnitario=request.POST["precio"],
                subTotal=request.POST["precio"],
            )
            detalle.save()

            # Embarque
            embarque = Embarque.objects.create(
                numDocumento=incrementa(request, "PA")["correlativo"],
                programacionViaje=viajeProgramado,
                venta=venta,
                pasajero_id=request.POST["pasajero"],
                lugar_abordo_id=request.POST["lugar_abordo"],
                lugar_bajada_id=request.POST["lugar_bajada"],
                hora_abordo=request.POST["hora_abordo"],
                observacion=request.POST["observacion"],
                numAsiento=request.POST["numAsiento"],
                precio=request.POST["precio"],
                telefono=request.POST["telefono"],
                usuario=request.user.persona,
            )

            # Actualizar estado asiento
            progasiento = ProgramacionAsiento.objects.get(id=request.POST["idasiento"])
            progasiento.estado = "vendido"
            progasiento.save()

            idmov = venta.id
            parametro = {
                "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                "tipomov": "ventaPasaje",
                "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                "mov": idmov,
                "destCountry": "PER&opId=0&busType=Any",
            }
            return redirect(
                f"{reverse('tesoreria:tesoreria-movimiento-add')}?{urlencode(parametro)}"
            )

    context = {
        "boleto": embarque,
        "viajeProgramado": viajeProgramado,
        "asientoProgramado": asientoProgramado,
        "anchoColumna": math.floor(11 / viajeProgramado.vehiculo.numColumnas),
    }

    return render(request, "apps/viaje/embarque/add.html", context)


def embarqueEdit(request):
    pasajero = get_object_or_404(Embarque, pk=request.GET.get("pk", 1))
    form = EmbarqueEditForm(instance=pasajero)
    if request.method == "POST":
        pasajero.enSala = True
        pasajero.save()
        return redirect("viaje:embarque-list")

    context = {"pasajero": form}
    return render(request, "apps/viaje/embarque/edit.html", context)


def embarqueCambiar(request):
    id = request.GET.get("pk", None)
    if id:
        embarque = get_object_or_404(Embarque, pk=id)
        embarque_form = EmbarqueEditForm(instance=embarque)

        if embarque:
            fech = embarque.programacionViaje.fechaViaje
            if fech < datetime.now().date():
                messages.info(request, "Tiene un día de retraso, no hay cambio...")
                return redirect("viaje:embarque-list")

            rutas = ProgramacionViaje.objects.filter(
                rutaOrigen=embarque.programacionViaje.rutaOrigen,
                rutaDestino=embarque.programacionViaje.rutaDestino,
                fechaViaje__gte=fech,
                activo=True,
            ).exclude(pk=embarque.programacionViaje.pk)
            # asientoProgramado = ProgramacionAsiento.objects.filter(programacionViaje=rutas.first()).order_by('asiento__codigoMatrix')

    if request.is_ajax():
        idprograma = request.GET.get("idprograma", None)
        if idprograma:
            data = []
            asientos = ProgramacionAsiento.objects.filter(
                programacionViaje__pk=idprograma
            ).order_by("asiento__codigoMatrix")
            nas = ""
            try:
                nas = math.floor(
                    11 / asientos.first().programacionViaje.vehiculo.numColumnas
                )
            except:
                messages.info(request, "No tiene Asientos programados")
            context = {"asientoProgramado": asientos, "anchoColumna": nas}
            return render(request, "apps/viaje/embarque/model_asiento.html", context)

        else:
            data = []
            for item in list(rutas):
                data.append(item.toJson())
            return JsonResponse({"data": data}, safe=False, status=200)

    if request.method == "POST":
        embarque_form = EmbarqueEditForm(request.POST, instance=embarque)
        if embarque_form.is_valid():
            em = embarque_form.save(commit=False)
            em.usuario = request.user.persona
            em.save()

            # actualizamos asiento
            asiento_program = get_object_or_404(
                ProgramacionAsiento, pk=request.POST.get("idasiento")
            )
            asiento_program.estado = "vendido"
            asiento_program.save()
            return redirect("viaje:embarque-list")

    context = {
        "rutas": rutas,
        "boleto": embarque_form,
    }
    return render(request, "apps/viaje/embarque/cambiar.html", context)


def embarquePrint(request):
    return render(request, "apps/viaje/embarque/print.html", context={})


def programa_add(request):
    form = ProgramacionViajeForm

    if request.method == "POST":
        form = ProgramacionViajeForm(request.POST)
        if form.is_valid():
            prog = form.save(commit=False)
            prog.activo = True
            prog.save()

            # crear los asientos
            for asiento in prog.vehiculo.asiento_set.all():
                ProgramacionAsiento.objects.create(
                    programacionViaje=prog,
                    asiento=asiento,
                    estado=asiento.estado,
                    precio=prog.precio,
                )

            # crear el manifiesto
            form_manifiesto = ManifiestoForm(request.POST)
            if form_manifiesto.is_valid():
                man = form_manifiesto.save(commit=False)
                man.numDocumento = incrementa(request, "MA")["correlativo"]
                man.programacionViaje = prog
                man.printRutaOrigen = prog.rutaOrigen
                man.save()

            else:
                messages.error(request, f"Algo salio mal, {form_manifiesto.errors}")

            idprogr = prog.id
            parametro = {
                "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                "tipomov": "encomiendaSalida",
                "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                "idproruta": idprogr,
                "destCountry": "PER&opId=0&busType=Any",
            }
            return redirect(
                f"{reverse('viaje:programa-asiento-list')}?{urlencode(parametro)}"
            )

    context = {"programa": form}

    return render(request, "apps/viaje/programa/add.html", context)


def programaEdit(request):
    idproruta = request.GET.get("idproruta")
    qr = get_object_or_404(ProgramacionViaje, pk=idproruta)
    fecha = qr.fechaViaje.strftime("%Y-%m-%d")
    hora = qr.horaViaje.strftime("%H:%M")

    programa = ProgramacionViajeForm(
        instance=qr, initial={"fechaViaje": fecha, "horaViaje": hora}
    )

    if request.method == "POST":
        form = ProgramacionViajeForm(request.POST, instance=qr)
        if form.is_valid():
            form.save()
            return redirect("viaje:programa-list")

    context = {"programa": programa, "idproruta": idproruta}
    return render(request, "apps/viaje/programa/edit.html", context)


def programaList(request):
    context = {}
    add_ruta_get = ""
    page = request.GET.get("page", 1)
    entity = ProgramacionViaje.objects.all().order_by("-fechaViaje")
    form = BuscarViajeForm
    verget = request.GET.get("rutaOrigen")

    if request.method == "POST":
        verget = ""
        form = BuscarViajeForm(request.POST)
        if form.is_valid():
            entity = ProgramacionViaje.objects.filter(
                rutaOrigen=form.cleaned_data["rutaOrigen"],
                rutaDestino=form.cleaned_data["rutaDestino"],
                fechaViaje=form.cleaned_data["fechaViaje"],
                activo=form.cleaned_data["activo"],
            ).order_by("-fechaViaje")

            add_ruta_get = f"""&rutaOrigen={form.cleaned_data["rutaOrigen"].id}&rutaDestino={form.cleaned_data["rutaDestino"].id}&fechaViaje={form.cleaned_data["fechaViaje"]}&activo={form.cleaned_data["activo"]}"""

            if not entity:
                messages.info(request, "No hay viaje para la fecha buscada!!")

        context["parametroBuscar"] = form

    # paginate con argumentos
    if verget:
        form = BuscarViajeForm(request.GET)

        entity = ProgramacionViaje.objects.filter(
            rutaOrigen=request.GET.get("rutaOrigen"),
            rutaDestino=request.GET.get("rutaDestino"),
            fechaViaje=request.GET.get("fechaViaje"),
            activo=request.GET.get("activo"),
        ).order_by("-fechaViaje")

        add_ruta_get = f"""&rutaOrigen={request.GET.get("rutaOrigen")}&rutaDestino={request.GET.get("rutaDestino")}&fechaViaje={request.GET.get("fechaViaje")}&activo={request.GET.get("activo")}"""

    # paginacion

    try:
        paginator = Paginator(entity, settings.NUM_PAGINATE)
        entity = paginator.page(page)
    except:
        # raise Http404
        entity = {}
        messages.info(request, "Se excedió en paginas")

    context = {
        "entity": entity,
        "parametroBuscar": form,
        "paginator": paginator,
        "add_ruta_get": add_ruta_get,
    }

    return render(request, "apps/viaje/programa/list.html", context)


def programaAsientoEdit(request):
    pk_asiento = request.GET.get("pk_asiento")
    asiento = get_object_or_404(ProgramacionAsiento, pk=pk_asiento)
    form_prog_asiento = ProgramacionAsientoForm(instance=asiento)
    if request.method == "POST":
        form_prog_asiento = ProgramacionAsientoForm(request.POST, instance=asiento)
        if form_prog_asiento.is_valid():
            form = form_prog_asiento.save(commit=False)
            form.save(update_fields=["estado", "precio"])

            asiento = get_object_or_404(ProgramacionAsiento, pk=pk_asiento)
            id = asiento.programacionViaje.id
            parametro = {
                "fromCityName": "chintucaycuri%20%28Todos%29&fromCityId=195648",
                "tipomov": "ventaPasaje",
                "toCityName": "Lima%20%28Todos%29&toCityId=195105&onward=20-Jan-2022&srcCountry=PER",
                "idproruta": id,
                "destCountry": "PER&opId=0&busType=Any",
            }
            return redirect(
                f"{reverse('viaje:programa-asiento-list')}?{urlencode(parametro)}"
            )

    context = {"form_prog_asiento": form_prog_asiento, "asiento": asiento}
    return render(request, "apps/viaje/programa/asiento-edit.html", context)


def programaAsientoList(request):
    pk_progr = request.GET.get("idproruta")
    viajeProgramado = get_object_or_404(ProgramacionViaje, pk=pk_progr)
    asientoProgramado = ProgramacionAsiento.objects.filter(
        programacionViaje=viajeProgramado
    ).order_by("asiento__codigoMatrix")

    context = {
        "idproruta": pk_progr,
        "asientoProgramado": asientoProgramado,
        "anchoColumna": math.floor(11 / viajeProgramado.vehiculo.numColumnas),
    }
    return render(request, "apps/viaje/programa/asiento-list.html", context)


def manifiestoEdit(request):
    idproruta = request.GET.get("idproruta")

    manifiesto = get_object_or_404(Manifiesto, programacionViaje=idproruta)
    embarques = Embarque.objects.filter(programacionViaje=idproruta).order_by("enSala")

    form = ManifiestoForm(
        instance=manifiesto,
        initial={"fechaViaje": manifiesto.programacionViaje.fechaViaje.isoformat()},
    )

    if request.method == "POST":
        idrutas = request.POST.get("idrutas").split(",")
        form = ManifiestoForm(request.POST, instance=manifiesto)
        if form.is_valid():
            man = form.save(commit=False)
            man.usuario = request.user.persona
            man.seGenero = True
            man.save()
            man.printRutaFinal.clear()
            for ruta in idrutas:
                man.printRutaFinal.add(ruta)
    idrutasdestino = []
    for x in manifiesto.printRutaFinal.all():
        idrutasdestino.append(x.id)

    context = {
        "form": form,
        "manifiesto": manifiesto,
        "embarques": embarques,
        "idrutasdestino": ",".join(map(str, idrutasdestino)),
    }
    return render(request, "apps/viaje/manifiesto/edit.html", context)


def manifiestoPrint(request):
    idproruta = request.GET.get("idproruta")
    sala = request.GET.get("sala", None)
    manifiesto = get_object_or_404(Manifiesto, programacionViaje=idproruta)

    if sala is None:
        embarques = Embarque.objects.filter(programacionViaje=idproruta).order_by(
            "enSala"
        )
    else:
        embarques = Embarque.objects.filter(programacionViaje=idproruta, enSala=sala)

    context = {
        "manifiesto": manifiesto,
        "embarques": embarques,
    }

    pdf = render_to_pdf("apps/viaje/manifiesto/print.html", context)
    return HttpResponse(pdf, content_type="application/pdf")

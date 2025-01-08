from datetime import datetime, date
import json

from django.conf import settings
import requests
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import transaction
from desatendidos.convertData import toJSON
from apps.persona.forms import PersonaForm, PersonaNaturalForm
from .models import Persona, PersonaJuridica, PersonaNatural
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Max, Min, Sum
from desatendidos import happyDay
from django.db.models import (
    IntegerField,
    DateField,
    ExpressionWrapper,
    F,
    DateTimeField,
)
from django.db.models.functions import TruncDate, Trunc, ExtractDay
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Persona, PersonaNatural, PersonaJuridica
from .serializers import (
    PersonaSerializer,
    PersonaNaturalSerializer,
    PersonaJuridicaSerializer,
)


def updateOrdenHappy(request):
    data = PersonaNatural.objects.all()
    for pers in data:
        if pers.fechaNac:
            pers.saveOrdenCumpl()

    return redirect("persona:list")


def listHappy(request):
    data = (
        PersonaNatural.objects.all()
        .filter(ordenhappy__gte=int(datetime.now().strftime("%j")))
        .order_by("ordenhappy")
    )

    page = request.GET.get("page", 1)
    q = request.GET.get("q", "")
    add_ruta_get = ""

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

    return context


def list(request):
    context = {}
    data = Persona.objects.all()
    page = request.GET.get("page", 1)
    search = request.GET.get("q")

    if search:
        try:

            data = Persona.objects.filter(
                Q(denominacion__icontains=search) | Q(numDoc__icontains=search)
            ).distinct()
            context["q"] = search
        except:
            data = {}

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

    context["entity"] = data
    context["paginator"] = paginator

    return render(request, "apps/persona/list.html", context)


def add(request):
    form = PersonaForm(initial={"tipoDoc": 1})
    form_natural = PersonaNaturalForm
    if request.method == "POST":
        form = PersonaForm(request.POST)
        tipo_doc = request.POST.get("tipoDoc")

        if tipo_doc != "2":
            print("no es ruc")
            form_natural = PersonaNaturalForm(request.POST, request.FILES)

            if form.is_valid() and form_natural.is_valid():
                with transaction.atomic():
                    per = form.save(commit=False)  # .save(commit=False)
                    per.activo = True
                    per.denominacion = f"{form_natural.cleaned_data['nombres']} {form_natural.cleaned_data['apellidoP']} {form_natural.cleaned_data['apellidoM']}"
                    per.save()

                    pn = form_natural.save(commit=False)
                    pn.persona = per
                    pn.save()
                    if pn.fechaNac:
                        pn.saveOrdenCumpl()

                    messages.success(request, "Se a creado correctamente")
                    return redirect("persona:list")
        else:
            print("si es ruc")
            if form.is_valid():
                with transaction.atomic():
                    per = form.save(commit=False)  # .save(commit=False)
                    per.activo = True
                    per.save()

                    PersonaJuridica.objects.create(persona=per)

                    messages.success(request, "Se a creado correctamente")
                    return redirect("persona:list")
    context = {"form": form, "form_natural": form_natural}

    return render(request, "apps/persona/add.html", context)


def edit(request, pk):
    context = {}
    person = get_object_or_404(Persona, pk=pk)
    context["form"] = PersonaForm(instance=person)
    if person.tipoDoc.codigo != "6":
        try:
            pn = person.personanatural
            if pn.fechaNac is not None:
                pn.fechaNac = pn.fechaNac.isoformat()
            context["form_natural"] = PersonaNaturalForm(instance=pn)

        except:
            messages.error(request, "No esta asociado con persona natural")
            return redirect("persona:list")

    if request.method == "POST":
        form = PersonaForm(request.POST, instance=person)

        if request.POST.get("tipoDoc") == str(person.tipoDoc.id):
            if form.is_valid():
                per = form.save(commit=False)

            if person.tipoDoc.codigo != "6":

                form_natural = PersonaNaturalForm(
                    request.POST, request.FILES, instance=person.personanatural
                )
                if form_natural.is_valid():
                    form_natural.save()
                    per.denominacion = f"{form_natural.cleaned_data['nombres']} {form_natural.cleaned_data['apellidoP']} {form_natural.cleaned_data['apellidoM']}"
            per.save()
            return redirect("persona:list")
        else:
            messages.info(request, "No se permite cambiar el Tipo de Documento")
            return redirect("persona:edit", pk=pk)

    return render(request, "apps/persona/edit.html", context)


def autocomplite(request):
    action = request.GET.get("action", None)
    term = request.GET.get("term", None)
    filtro = request.GET.get("filtro", None)

    if action == "autocomplete" and term is not None:
        data = []

        filt = None
        if filtro == "personal":
            filt = Q(ispersonal=True)

        # Crea la base de la consulta
        query = Q(denominacion__icontains=term) | Q(numDoc__icontains=term)

        # Si filt no es None, combina con el filtro de la consulta
        if filt is not None:
            query = query & filt  # Combina con AND

        # Realiza la consulta
        personas = Persona.objects.filter(query).distinct()[:10]

        if personas:
            for i in personas:
                item = i.toJSON()
                item["text"] = i.denominacion
                data.append(item)
        else:
            data["error"] = "No hay datos"

        return JsonResponse(data, safe=False)


@csrf_exempt
def buscarApiDoc(request):
    data = {}
    url_ruc = "https://api.apis.net.pe/v1/ruc?numero="
    url_dni = "https://consulta.api-peru.com/api/dni/"
    # url_dni_op2 = 'https://www.mef.gob.pe/ventanilla/api/mefconsultapersona/'
    # url_dni_op2 = 'https://apps.mineco.gob.pe/ventanilla/api/mefconsultapersona/'
    # url_dni_op2 = 'https://backend.cooperativacultural.com.pe/api/caja/functions/datosdni/?numero='

    if request.method == "POST":
        datos = json.loads(request.body)
        if datos["tipodoc"] == "DNI":

            response = requests.get(f"{url_dni}{datos['numdoc']}").json()
            if not response["success"]:
                url_dni_op2 = f'https://apps.mineco.gob.pe/ventanilla/api/mefconsultapersona/{datos["numdoc"]}/01/'
                response = requests.get(url_dni_op2).json()
                response = response["objeto"]
                if not response:
                    data["error"] = "Fallo la busqueda, ingrese los datos manualmente.."
                    return JsonResponse(data, safe=False)

                data["denominacion"] = (
                    f"{response['nat_Nombres']} {response['nat_Ape_Pat']} {response['nat_Ape_Mat']}"
                )
                data["direccion"] = ""
                data["nombres"] = response["nat_Nombres"]
                data["apellido_paterno"] = response["nat_Ape_Pat"]
                data["apellido_materno"] = response["nat_Ape_Mat"]
                data["sexo"] = "M"
                data["fecha_nacimiento"] = ""

                """url_dni2=f'{url_dni_op2}{datos["numdoc"]}/01'
                                                                response = requests.get(url_dni2).json()
                                                                print(type(response))
                                                                print(response['objeto'])
                                                                if response['error_lista']:
                                                                    data['error'] = 'Fallo la busqueda, ingrese los datos manualmente..'
                                                                    return JsonResponse(data, safe = False)
                                                
                                                                data['denominacion']= f"{response['objeto']['nat_Nombres']} {response['objeto']['nat_Ape_Pat']} {response['objeto']['nat_Ape_Mat']}"
                                                                data['direccion']= ''
                                                                data['nombres']= response['objeto']['nat_Nombres']
                                                                data['apellido_paterno']= response['objeto']['nat_Ape_Pat']
                                                                data['apellido_materno']= response['objeto']['nat_Ape_Mat']
                                                                data['sexo']= 'M' 
                                                                data['fecha_nacimiento']= ''"""

            else:
                data["denominacion"] = response["data"]["nombre_completo"]
                data["direccion"] = ""
                data["nombres"] = response["data"]["nombres"]
                data["apellido_paterno"] = response["data"]["apellido_paterno"]
                data["apellido_materno"] = response["data"]["apellido_materno"]
                data["sexo"] = "M" if response["data"]["sexo"] == "MASCULINO" else "F"
                data["fecha_nacimiento"] = response["data"]["fecha_nacimiento"]

        elif datos["tipodoc"] == "RUC":
            response = requests.get(f"{url_ruc}{datos['numdoc']}", verify=True).json()
            data["denominacion"] = response["nombre"]
            data["direccion"] = response["direccion"]
            data["ubigeo"] = response["ubigeo"]
            data["distrito"] = response["distrito"]
            data["provincia"] = response["provincia"]
            data["departamento"] = response["departamento"]
        else:
            data["error"] = "parametros incorrectos"

    return JsonResponse(data, safe=False)


class PersonaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


class PersonaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer

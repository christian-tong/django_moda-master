import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Sum
from apps.caja.models import MovimientoCaja
from .forms import UsuarioForm, UsuarioLoginForm, UsuarioAgenciaForm
from .models import Menu, Usuario
from apps.persona.models import Persona
from apps.persona.views import listHappy


def userList(request):
    users = Usuario.objects.all()
    context = {
        "entity": users,
    }

    return render(request, "apps/sistema/usuario/list.html", context)


def userAdd(request):
    user = UsuarioForm()

    if request.method == "POST":
        user = UsuarioForm(request.POST)
        if user.is_valid():
            us = user.save(commit=False)
            us.date_joined = datetime.datetime.now()
            us.set_password(user.cleaned_data.get("password"))
            us.save()

            return redirect("sistema:user-list")

    context = {"usuario": user}
    return render(request, "apps/sistema/usuario/add.html", context)


def accountLogin(request):
    dataLogin = UsuarioLoginForm

    if request.method == "POST":
        dataLogin = UsuarioLoginForm(request.POST)
        if dataLogin.is_valid():
            username = dataLogin.cleaned_data.get("username")
            password = dataLogin.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None and user.is_active:
                login(request, user)
                ag = Usuario.objects.get(id=request.user.id).agencia.all()

                if ag:
                    if len(ag) == 1:
                        request.session["agencia_id"] = ag[0].id
                        request.session["agencia_nombre"] = ag[0].nombre
                        request.session["agencia_uno"] = True
                        return redirect("sistema:home-index")
                    else:
                        return redirect("sistema:user-agencia-list")
                else:
                    messages.error(
                        request,
                        "Accedio con exito, pero no tiene una agencia a cargo!!",
                    )
            else:
                messages.error(request, "El usuario o la contraseña esta mal!!")

    context = {
        "login": dataLogin,
    }

    return render(request, "apps/sistema/account/login.html", context)


def accountLoggout(request):

    logout(request)
    del request.session

    return redirect("web:index")


def menuList(request):
    if (
        request.method == "GET"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
    ):
        menus = Menu.objects.filter(padre=None).order_by("orden")
        items = {}
        for menu in menus:
            subitem = {}
            subitem["padre"] = list(Menu.objects.filter(id=menu.id).values())
            subitem["hijo"] = list(
                Menu.objects.filter(padre=menu).order_by("orden").values()
            )
            items[menu.nombre] = subitem

        return JsonResponse(items, safe=False, status=200)

    return JsonResponse({"success": False}, status=400)


def userAgencia(request):
    form = UsuarioAgenciaForm(request=request)

    if request.method == "POST":
        form = UsuarioAgenciaForm(request.POST, request=request)
        if form.is_valid():
            request.session["agencia_id"] = form.cleaned_data.get("agencia").id
            request.session["agencia_nombre"] = form.cleaned_data.get("agencia").nombre

            return redirect("sistema:home-index")
        else:
            print("+++++++++++no es valid")

    context = {"agencias": form}
    return render(request, "apps/sistema/usuario/list-agencia.html", context)


def homeIndex(request):
    tclientes = Persona.objects.all().count()
    stingresos = MovimientoCaja.objects.filter(tipoMov__tipo="ingreso").aggregate(
        Sum("monto")
    )["monto__sum"]
    tingresos = stingresos if stingresos != None else 0
    stegresos = MovimientoCaja.objects.filter(tipoMov__tipo="egreso").aggregate(
        Sum("monto")
    )["monto__sum"]
    tegresos = stegresos if stegresos != None else 0
    saldo = tingresos - tegresos

    hapyday = listHappy(request)
    context = {
        "tclientes": tclientes,
        "tingresos": tingresos,
        "tegresos": tegresos,
        "saldo": saldo,
        "entity": hapyday["entity"],
        "paginator": hapyday["paginator"],
        "add_ruta_get": hapyday["add_ruta_get"],
        "q": hapyday["q"],
    }
    return render(request, "apps/sistema/home/index.html", context)


def custom_permission_denied_view(request, exception):
    return render(request, "layouts/403.html", status=403)

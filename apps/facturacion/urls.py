from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import boletaPrint, list, enviarOse, detallePrint, ComprobanteExcel

app_name = "facturacion"
urlpatterns = [
    path("list/", login_required(list), name="list"),
    path("boleta/print/", login_required(boletaPrint), name="boleta-print"),
    path("detalle/print/", login_required(detallePrint), name="detalle-print"),
    path("enviar/ose/<int:pk>", login_required(enviarOse), name="enviar-ose"),
    path(
        "comprobante/excel/", login_required(ComprobanteExcel), name="comprobante-excel"
    ),
]

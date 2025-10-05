# BACKEND apps\facturacion\api\views.py

import io
import qrcode
import qrcode.image.svg
from django.db.models import Q
from django.template.loader import get_template
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from apps.facturacion.models import FaturaBoleta
from apps.venta.models import Movimiento
from apps.empresa.models import Agencia
from desatendidos.numeroLetras import numero_to_letras
from desatendidos.exportFile import FormatoExcel
from desatendidos.envioOse import logicaEnvioOse

from .serializers import (
    FaturaBoletaListSerializer,
    FaturaBoletaDetailSerializer,
    FaturaBoletaWriteSerializer,
)

# ====================================================
# 🔧 UTILITARIOS
# ====================================================


def ok(entity=None, message=None):
    return Response({"ok": True, "entity": entity, "message": message})


def fail(message=None):
    return Response({"ok": False, "entity": None, "message": message}, status=400)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# ====================================================
# 📄 VIEWSET PRINCIPAL
# ====================================================


class FaturaBoletaViewSet(viewsets.ModelViewSet):
    queryset = (
        FaturaBoleta.objects.all()
        .select_related("tipoDocumento", "cliente", "usuario", "ventaMovimiento")
        .order_by("-fechaFact", "-id")
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return FaturaBoletaListSerializer
        elif self.action == "retrieve":
            return FaturaBoletaDetailSerializer
        return FaturaBoletaWriteSerializer

    # ------------------------------------------------
    # 🔹 LISTAR
    # ------------------------------------------------
    def list(self, request):
        q = request.GET.get("q")
        qs = self.get_queryset()
        if q:
            qs = qs.filter(
                Q(cliente__denominacion__icontains=q) | Q(cliente__numDoc__icontains=q)
            )
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": ser.data})

    # ------------------------------------------------
    # 📦 Enviar OSE (Nubefact)
    # ------------------------------------------------
    @action(detail=True, methods=["post"], url_path="enviar-ose")
    def enviar_ose(self, request, pk=None):
        factura = self.get_object()
        try:
            req = logicaEnvioOse(factura.ventaMovimiento.id, factura, True)
        except Exception as e:
            return fail(f"Error al conectar con OSE: {e}")

        if req.get("errors"):
            return fail(f"Error OSE: {req['errors']}")
        return ok(message="Documento enviado correctamente a OSE ✅")

    # ====================================================
    # 🧾 PRINT BOLETA (solo HTML)
    # ====================================================
    @action(detail=True, methods=["get"], url_path="print")
    def print_boleta(self, request, pk=None):
        """Devuelve la vista HTML SOLO de la boleta."""
        factura = self.get_object()
        movimiento = factura.ventaMovimiento
        principal = Agencia.objects.filter(tipo="PRINCIPAL").first()

        # QR
        image_qr = None
        if not factura.estaFacturado:
            req = logicaEnvioOse(movimiento.id, factura, False)
            if not req or req.get("errors"):
                return fail(
                    f"Error al facturar: {req.get('errors', 'Error desconocido')}"
                )
            factura.cadenaqr = req.get("cadena_para_codigo_qr")
            factura.estaFacturado = True
            factura.save()

        if factura.cadenaqr:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(factura.cadenaqr, image_factory=factory, box_size=5)
            stream = io.BytesIO()
            img.save(stream)
            image_qr = stream.getvalue().decode()

        totales = getattr(
            getattr(movimiento, "embarque", None), "precio", factura.monto
        )

        context = {
            "factura": factura,
            "movimiento": movimiento,
            "image_qr": image_qr,
            "num_letras": numero_to_letras(totales),
            "totales": totales,
            "principal": principal,
        }

        html = get_template("apps/facturacion/print-boleta.html").render(context)
        return HttpResponse(html)

    # ====================================================
    # 📦 PRINT DETALLE (solo HTML)
    # ====================================================
    @action(detail=True, methods=["get"], url_path="print-detalle")
    def print_detalle(self, request, pk=None):
        """Devuelve la vista HTML SOLO del detalle (embarque o guía)."""
        factura = self.get_object()
        movimiento = factura.ventaMovimiento
        principal = Agencia.objects.filter(tipo="PRINCIPAL").first()

        image_qr = None
        if factura.cadenaqr:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(factura.cadenaqr, image_factory=factory, box_size=5)
            stream = io.BytesIO()
            img.save(stream)
            image_qr = stream.getvalue().decode()

        tipomovi = (
            "encomiendaSalida" if hasattr(movimiento, "encomienda") else "ventaPasaje"
        )
        totales = getattr(
            getattr(movimiento, "encomienda", None),
            "precio",
            getattr(getattr(movimiento, "embarque", None), "precio", factura.monto),
        )

        context = {
            "factura": factura,
            "movimiento": movimiento,
            "image_qr": image_qr,
            "num_letras": numero_to_letras(totales),
            "totales": totales,
            "principal": principal,
            "tipomovi": tipomovi,
        }

        html = get_template("apps/facturacion/print-detalle.html").render(context)
        return HttpResponse(html)

    # ====================================================
    # 📊 Exportar Comprobante Excel
    # ====================================================
    @action(detail=False, methods=["get"], url_path="comprobante/excel")
    def comprobante_excel(self, request):
        periodo = request.GET.get("periodo")
        year, mes = int(periodo[:4]), int(periodo[5:])
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
            fechaFact__year=year,
            fechaFact__month=mes,
            estaFacturado=True,
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
        return FormatoExcel(columns, obj, "export-comprobantes", f"documento-{periodo}")

import requests
import json
from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from apps.venta.models import Movimiento
from apps.empresa.models import AgenciaDocumento


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)


def logicaEnvioOse(pk, factura, canje):
    url = "https://api.nubefact.com/api/v1/531f1e3e-1499-41d9-a89c-bbcda206a0ff"
    auth_token = "19d6603003dd4839b0f064691186da73138b97776c764fb595803de549b1e62f"
    head = {"Authorization": auth_token, "content-type": "application/json"}
    data = archivoJsonOse(pk)
    if data["error"]:
        return JsonResponse({"data": "Error en armar json"}, safe=False)

    response = requests.post(
        url, data=json.dumps(data["documento"], cls=CustomJsonEncoder), headers=head
    )

    req = response.json()

    if req.get("errors") is None:
        factura.serie = req.get("serie")
        factura.numero = req.get("numero")
        factura.fechaFact = datetime.today().strftime("%d-%m-%Y")
        factura.estaFacturado = True
        factura.iscanje = True if canje else False
        factura.enlace = req.get("enlace_del_pdf")
        factura.cadenaqr = req.get("cadena_para_codigo_qr")
        factura.save()

        movimiento = get_object_or_404(Movimiento, pk=pk)
        correlativo = AgenciaDocumento.objects.get(
            documento=movimiento.faturaboleta.tipoDocumento.pk,
            agencia__tipo="PRINCIPAL",
        )
        correlativo.correlativoMas()

    return req


def archivoJsonOse(pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    data = {"error": True}
    if (
        movimiento.faturaboleta.tipoDocumento.codigo == "01"
        or movimiento.faturaboleta.tipoDocumento.codigo == "03"
    ):
        correlat = AgenciaDocumento.objects.get(
            documento=movimiento.faturaboleta.tipoDocumento.pk,
            agencia__tipo="PRINCIPAL",
        )

        documento = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": f"{movimiento.faturaboleta.tipoDocumento.codOse}",
            "serie": f"{correlat.serie}",
            "numero": correlat.correlativo,
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": movimiento.faturaboleta.cliente.tipoDoc.codOse,
            "cliente_numero_de_documento": f"{movimiento.faturaboleta.cliente.numDoc}",
            "cliente_denominacion": f"{(movimiento.faturaboleta.cliente.denominacion).upper()}",
            "cliente_direccion": "-"
            if movimiento.faturaboleta.cliente.direccion is None
            else f"{movimiento.faturaboleta.cliente.direccion}",
            "cliente_email": "",
            "cliente_email_1": "",
            "cliente_email_2": "",
            "fecha_de_emision": f"{datetime.today().strftime('%d-%m-%Y')}",
            "fecha_de_vencimiento": "",
            "moneda": "1",
            "tipo_de_cambio": "",
            "porcentaje_de_igv": "18.00",
            "descuento_global": "",
            "total_descuento": "",
            "total_anticipo": "",
            "total_gravada": "",
            "total_inafecta": "",
            "total_exonerada": movimiento.faturaboleta.monto,
            "total_igv": "",
            "total_gratuita": "",
            "total_otros_cargos": "",
            "total": movimiento.faturaboleta.monto,
            "percepcion_tipo": "",
            "percepcion_base_imponible": "",
            "total_percepcion": "",
            "total_incluido_percepcion": "",
            "detraccion": "false",
            "observaciones": "",
            "documento_que_se_modifica_tipo": "",
            "documento_que_se_modifica_serie": "",
            "documento_que_se_modifica_numero": "",
            "tipo_de_nota_de_credito": "",
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": "true",
            "enviar_automaticamente_al_cliente": "false",
            "codigo_unico": "",
            "condiciones_de_pago": "",
            "medio_de_pago": "",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "tabla_personalizada_codigo": "",
            "formato_de_pdf": "",
        }
        documento["items"] = []

        for item in movimiento.detallemov_set.all():
            items = {
                "unidad_de_medida": f"{item.unidadMedida}",
                "codigo": "001",
                "descripcion": f"{item.descripcion}",
                "cantidad": item.cantidad,
                "valor_unitario": item.valorUnitario,
                "precio_unitario": item.valorUnitario,
                "descuento": "",
                "subtotal": item.subTotal,
                "tipo_de_igv": "8",
                "igv": "0",
                "total": item.subTotal,
                "anticipo_regularizacion": "false",
                "anticipo_documento_serie": "",
                "anticipo_documento_numero": "",
                "codigo_producto_sunat": "10000000",
            }

            documento["items"].append(items)

        data["documento"] = documento
        data["error"] = False

    return data

# BCAKEND apps\envio\api\views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum
from django.template.loader import get_template
from django.http import HttpResponse

from apps.envio.models import Encomienda, Liquidacion, ClienteRecepcion
from apps.envio.api.serializers import (
    EncomiendaListSerializer,
    EncomiendaDetailSerializer,
    EncomiendaWriteSerializer,
    LiquidacionListSerializer,
    LiquidacionDetailSerializer,
    LiquidacionWriteSerializer,
)

from apps.envio.views import liquidacionRecepcion

from rest_framework.parsers import JSONParser


# ==========================================================
# PAGINACIÓN ESTÁNDAR
# ==========================================================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 200


# ==========================================================
# UTILITARIOS
# ==========================================================
def ok(entity=None, message=None, status_code=status.HTTP_200_OK):
    return Response(
        {"ok": True, "entity": entity, "message": message, "errors": None},
        status=status_code,
    )


def fail(errors=None, message=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {"ok": False, "entity": None, "message": message, "errors": errors},
        status=status_code,
    )


def camel_to_label(name: str) -> str:
    """
    Convierte nombres tipo 'agenciaDestino' o 'numeroContacto'
    en 'Agencia Destino' o 'Número Contacto'.
    """
    parts = []
    current = name[0].upper()
    for c in name[1:]:
        if c.isupper():
            parts.append(current)
            current = c
        else:
            current += c
    parts.append(current)
    return " ".join(parts)


# ==========================================================
# ENCOMIENDA VIEWSET
# ==========================================================
class EncomiendaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Encomienda con búsqueda, impresión y recepción.
    """

    queryset = Encomienda.objects.all().select_related(
        "remite", "consignado", "agenciaOrigen", "agenciaDestino", "venta"
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["list"]:
            return EncomiendaListSerializer
        elif self.action in ["retrieve", "recepcion_data"]:
            return EncomiendaDetailSerializer
        return EncomiendaWriteSerializer

    # ==========================================================
    # LISTADO GENERAL CON FECHAS
    # ==========================================================
    def list(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        qs = self.queryset

        if q:
            qs = qs.filter(
                Q(numDocumento__icontains=q)
                | Q(remite__denominacion__icontains=q)
                | Q(consignado__denominacion__icontains=q)
                | Q(agenciaOrigen__nombre__icontains=q)
                | Q(agenciaDestino__nombre__icontains=q)
                | Q(numeroContacto__icontains=q)
                | Q(estado__icontains=q)
            )

        # 🔽 ordenadas de más recientes a más antiguas
        qs = qs.order_by("-id")

        # 🔁 Serialización base
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        data = serializer.data

        # ➕ Post-procesamiento: agregar fechas y labels legibles
        for item in data:
            encomienda = qs.filter(id=item["id"]).first()
            if encomienda:
                venta = getattr(encomienda, "venta", None)
                recep = getattr(encomienda, "clienterecepcion", None)
                item["fechaCreacion"] = venta.create.isoformat() if venta else None
                item["fechaRecepcion"] = recep.fecha.isoformat() if recep else None

        return self.get_paginated_response({"entity": data})

    # ==========================================================
    # 📄 IMPRESIÓN DETALLE
    # ==========================================================
    @action(detail=True, methods=["get"], url_path="print-detalle")
    def print_encomienda_detalle(self, request, pk=None):
        """
        Devuelve el HTML del comprobante PDF.
        """
        encomienda = self.get_object()
        total = (
            encomienda.venta.detallemov_set.all().aggregate(Sum("subTotal"))[
                "subTotal__sum"
            ]
            or 0
        )
        context = {"encomienda": encomienda, "total": total}
        html = get_template("apps/envio/encomienda/print-detalle.html").render(context)
        return HttpResponse(html)

    # ==========================================================
    # 📦 RECEPCIÓN - obtener datos (GET)
    # ==========================================================
    @action(detail=True, methods=["get"], url_path="recepcion-data")
    def recepcion_data(self, request, pk=None):
        encomienda = self.get_object()
        venta = encomienda.venta

        # 🧾 Detalles
        detalles = (
            list(
                venta.detallemov_set.all().values(
                    "id", "cantidad", "descripcion", "valorUnitario", "subTotal"
                )
            )
            if venta
            else []
        )

        # 🕒 Fechas
        fecha_creacion = venta.create if venta else None
        recepcion_existente = getattr(encomienda, "clienterecepcion", None)
        fecha_recepcion = recepcion_existente.fecha if recepcion_existente else None
        evidencia_url = (
            recepcion_existente.evidencia.url
            if recepcion_existente and recepcion_existente.evidencia
            else None
        )

        entity = {
            "id": encomienda.id,
            "numDocumento": encomienda.numDocumento,
            "agenciaOrigen": str(encomienda.agenciaOrigen),
            "agenciaDestino": str(encomienda.agenciaDestino),
            "remite": str(encomienda.remite),
            "consignado": str(encomienda.consignado),
            "esContraEntrega": encomienda.esContraEntrega,
            "aDomicilio": encomienda.aDomicilio,
            "domicilio": encomienda.domicilio,
            "precio": encomienda.precio,
            "observacion": encomienda.observacion,
            "estado": encomienda.estado,
            "fechaCreacion": fecha_creacion,
            "fechaRecepcion": fecha_recepcion,
            "detalles": detalles,
            "yaRecepcionado": bool(recepcion_existente),
            "evidencia": evidencia_url,
        }
        return ok(entity)

    # ==========================================================
    # 🧾 OBTENER CORRELATIVO SIGUIENTE (auto incrementable)
    # ==========================================================
    @action(detail=False, methods=["get"], url_path="next-numero")
    def next_numero(self, request):
        """
        Devuelve el correlativo actual o el siguiente número de encomienda.
        Si el documento de agencia no lleva control, se calcula
        en base al último número de Encomienda registrado.
        """
        from apps.empresa.models import Agencia, AgenciaDocumento

        try:
            # 1️⃣ Determinar agencia actual
            agencia_id = request.session.get("agencia_id")
            if agencia_id:
                agencia_obj = Agencia.objects.filter(id=agencia_id).first()
            else:
                agencia_obj = Agencia.objects.filter(activo=True).first()

            if not agencia_obj:
                return fail(message="No hay agencias activas registradas.")

            # 2️⃣ Buscar documento EN (encomienda)
            agencia_doc = AgenciaDocumento.objects.filter(
                agencia=agencia_obj, documento__codigo="EN"
            ).first()

            # 3️⃣ Intentar obtener correlativo desde agencia_doc
            correlativo_doc = None
            if agencia_doc and hasattr(agencia_doc, "correlativo"):
                correlativo_doc = agencia_doc.correlativo

            # 4️⃣ Si el documento no tiene correlativo o está desactualizado,
            # buscar el último número usado en Encomienda
            correlativo_db = None
            ultima_encomienda = (
                Encomienda.objects.filter(agenciaOrigen=agencia_obj)
                .exclude(numDocumento__isnull=True)
                .exclude(numDocumento__exact="")
                .order_by("-id")
                .first()
            )
            if ultima_encomienda:
                try:
                    correlativo_db = int(ultima_encomienda.numDocumento)
                except (ValueError, TypeError):
                    correlativo_db = None

            # 5️⃣ Determinar el correlativo siguiente
            if correlativo_db and (
                not correlativo_doc or correlativo_db >= correlativo_doc
            ):
                next_num = correlativo_db + 1
                source = "BD (último registro)"
            elif correlativo_doc:
                next_num = correlativo_doc + 1
                source = "AgenciaDocumento"
            else:
                next_num = 1
                source = "Fallback inicial"

            # 6️⃣ Respuesta estándar
            return ok(
                {"numEncomienda": next_num},
                message=f"Correlativo obtenido desde {source} para {agencia_obj.nombre}.",
            )

        except Exception as e:
            return fail(message=f"Error al obtener correlativo: {str(e)}")

    # ==========================================================
    # 🗑️ ELIMINAR ENCOMIENDA
    # ==========================================================

    @action(detail=True, methods=["delete"], url_path="eliminar")
    def eliminar_encomienda(self, request, pk=None):
        """
        Elimina una encomienda y su venta relacionada, si no está recepcionada.
        """
        try:
            encomienda = self.get_object()

            # 🔒 Validaciones
            if encomienda.estado == "recepcionado":
                return fail(message="No se puede eliminar una encomienda recepcionada.")
            if encomienda.estado == "enCamino":
                return fail(message="No se puede eliminar una encomienda en camino.")

            # 🧾 Eliminar venta asociada si existe
            venta = getattr(encomienda, "venta", None)
            if venta:
                venta.delete()

            encomienda.delete()
            return ok(message=f"Encomienda {pk} eliminada correctamente.")

        except Encomienda.DoesNotExist:
            return fail(message="La encomienda no existe.")
        except Exception as e:
            return fail(message=f"Error al eliminar encomienda: {str(e)}")

    @action(detail=False, methods=["get"], url_path="unidad-medida")
    def unidad_medida(self, request):
        """
        Devuelve las opciones de unidad de medida disponibles.
        """
        unidades = [
            {"codigo": "NIU", "descripcion": "Unidad"},
            {"codigo": "ZZ", "descripcion": "Servicio"},
        ]
        return ok(unidades)

    @action(detail=False, methods=["post"], url_path="crear-completo")
    def crear_completo(self, request):
        """
        Crea una encomienda completa (Movimiento + Detalle + Encomienda),
        aplicando el correlativo real de la agencia (como el HTML original).
        """
        from apps.venta.models import Movimiento, DetalleMov
        from apps.empresa.models import Agencia, AgenciaDocumento

        data = request.data
        try:
            persona = request.user.persona

            # 🧭 1. Determinar agencia origen (o la activa)
            agencia_id = data.get("agenciaOrigen") or request.session.get("agencia_id")
            agencia_usuario = Agencia.objects.filter(id=agencia_id).first()
            if not agencia_usuario:
                agencia_usuario = Agencia.objects.filter(activo=True).first()

            if not agencia_usuario:
                return fail(
                    message="No se encontró agencia válida para generar el correlativo."
                )

            # 🧾 2. Obtener o generar correlativo
            agencia_doc = AgenciaDocumento.objects.filter(
                agencia=agencia_usuario, documento__codigo="EN"
            ).first()

            if not agencia_doc:
                return fail(
                    message=f"No se encontró documento EN para la agencia {agencia_usuario.nombre}."
                )

            # Si viene numDocumento desde frontend, respétalo
            num_doc = data.get("numDocumento") or agencia_doc.correlativoMas()

            # 💾 3. Crear movimiento
            venta = Movimiento.objects.create(vendedor=persona, agencia=agencia_usuario)

            # 💾 4. Crear detalle
            cantidad = float(data.get("cantidad", 1))
            valor_unitario = float(data.get("valorUnitario", 0))
            subtotal = cantidad * valor_unitario

            DetalleMov.objects.create(
                movimiento=venta,
                unidadMedida=data.get("unidadMedida", "NIU"),
                cantidad=cantidad,
                descripcion=data.get("descripcion", ""),
                valorUnitario=valor_unitario,
                subTotal=subtotal,
            )

            # 💾 5. Crear encomienda
            encomienda = Encomienda.objects.create(
                numDocumento=num_doc,
                venta=venta,
                remite_id=data.get("remite"),
                consignado_id=data.get("consignado"),
                agenciaOrigen_id=data.get("agenciaOrigen"),
                agenciaDestino_id=data.get("agenciaDestino"),
                esContraEntrega=data.get("esContraEntrega", False),
                aDomicilio=data.get("aDomicilio", False),
                domicilio=data.get("domicilio", ""),
                seguridadClave=data.get("seguridadClave", ""),
                observacion=data.get("observacion", ""),
                estado="agenciaOrigen",
                precio=subtotal,
                numeroContacto=data.get("numeroContacto", ""),
            )

            # 💹 6. Retornar y actualizar correlativo
            serializer = EncomiendaDetailSerializer(encomienda)
            return ok(
                serializer.data,
                message=f"Encomienda registrada correctamente con número {num_doc}.",
            )

        except Exception as e:
            return fail(message=f"Error al registrar encomienda: {str(e)}")

    # ==========================================================
    # 📦 VALIDAR CLAVE (nuevo)
    # ==========================================================
    @action(detail=True, methods=["post"], url_path="validar-clave")
    def validar_clave(self, request, pk=None):
        """
        Valida si la clave ingresada coincide con la encomienda.
        """
        encomienda = self.get_object()
        clave = request.data.get("clave", "").strip()

        if not clave:
            return fail(message="Debe ingresar una clave.")
        if encomienda.seguridadClave != clave:
            return fail(message="Clave incorrecta.")
        if encomienda.estado == "recepcionado":
            return fail(message="Esta encomienda ya fue recepcionada previamente.")

        # ✅ Clave válida
        return ok(
            {"valid": True}, message="Clave válida. Puede proceder con la entrega."
        )

    # ==========================================================
    # 📦 RECEPCIÓN - registrar entrega (POST)
    # ==========================================================
    @action(detail=True, methods=["post"], url_path="recepcion")
    def recepcion_encomienda(self, request, pk=None):
        """
        Registra la entrega de una encomienda:
        - Verifica la clave de seguridad
        - Guarda evidencia (si se envía)
        - Cambia estado a 'recepcionado'
        """
        encomienda = self.get_object()
        clave = request.data.get("clave", "").strip()
        evidencia = request.FILES.get("evidencia", None)

        # 🧩 Validaciones
        if not clave:
            return fail(message="Debe ingresar la clave de seguridad.")
        if encomienda.seguridadClave != clave:
            return fail(message="Clave incorrecta.")
        if encomienda.estado == "recepcionado":
            return fail(message="La encomienda ya fue recepcionada previamente.")

        # 🧾 Crear registro de recepción
        recep = ClienteRecepcion.objects.create(
            encomienda=encomienda,
            usuario=request.user.persona,
            evidencia=evidencia,
        )

        # 🔄 Actualizar estado
        encomienda.estado = "recepcionado"
        encomienda.save(update_fields=["estado"])

        # 🧩 Respuesta final con evidencia URL
        evidencia_url = recep.evidencia.url if recep.evidencia else None

        return ok(
            {
                "id": encomienda.id,
                "estado": encomienda.estado,
                "fechaRecepcion": recep.fecha,
                "evidencia": evidencia_url,
            },
            message="Encomienda entregada correctamente.",
        )


# ==========================================================
# LIQUIDACIÓN VIEWSET
# ==========================================================


class LiquidacionViewSet(viewsets.ModelViewSet):
    """
    CRUD de Liquidación con paginación, búsqueda y acciones personalizadas.
    """

    queryset = Liquidacion.objects.all().select_related(
        "agenciaOrigen", "agenciaDestino", "vehiculo", "conductor"
    )
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    parser_classes = [JSONParser]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return LiquidacionListSerializer
        elif self.action in ["retrieve", "recepcion_data"]:
            return LiquidacionDetailSerializer
        return LiquidacionWriteSerializer

    # ------------------------------------------------------
    # 🔍 LISTADO GENERAL
    # ------------------------------------------------------
    def list(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        qs = self.queryset

        if q:
            qs = qs.filter(
                Q(numDocumento__icontains=q)
                | Q(agenciaOrigen__nombre__icontains=q)
                | Q(agenciaDestino__nombre__icontains=q)
                | Q(vehiculo__placa__icontains=q)
                | Q(conductor__chofer__denominacion__icontains=q)
                | Q(observacion__icontains=q)
            )

        qs = qs.order_by("-fecha")
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response({"entity": serializer.data})

    # ------------------------------------------------------
    # ➕ CREAR LIQUIDACIÓN CON CORRELATIVO DINÁMICO (POST)
    # ------------------------------------------------------
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva liquidación asegurando el correlativo correcto según
        la agencia de origen. Compatible con application/json.
        """
        from apps.empresa.models import AgenciaDocumento

        data = request.data
        serializer = LiquidacionWriteSerializer(data=data)
        if not serializer.is_valid():
            return fail(errors=serializer.errors)

        data = serializer.validated_data
        agencia_origen = data.get("agenciaOrigen")

        if not agencia_origen:
            return fail(message="Debe seleccionar una agencia de origen.")

        try:
            # 🔎 Buscar documento de tipo 'LI' (Liquidación) para la agencia
            agencia_doc = AgenciaDocumento.objects.filter(
                agencia=agencia_origen, documento__codigo="LI"
            ).first()

            # 🔢 Obtener correlativo actual desde base de datos
            ultima_liq = (
                Liquidacion.objects.filter(agenciaOrigen=agencia_origen)
                .exclude(numDocumento__isnull=True)
                .order_by("-numDocumento")
                .first()
            )
            correlativo_db = ultima_liq.numDocumento if ultima_liq else 0

            # 🧮 Determinar correlativo siguiente
            if agencia_doc and agencia_doc.correlativo:
                correlativo_doc = agencia_doc.correlativo
                if correlativo_db >= correlativo_doc:
                    next_num = correlativo_db + 1
                    source = "BD (último registro)"
                else:
                    next_num = correlativo_doc + 1
                    source = "AgenciaDocumento"
            else:
                next_num = correlativo_db + 1
                source = "Fallback inicial"

            # 💾 Crear la liquidación (evitando duplicidad)
            data.pop("numDocumento", None)  # 👈 evita el error de argumentos duplicados

            liq = Liquidacion.objects.create(
                numDocumento=next_num,
                usuario=request.user.persona,
                **data,
            )

            # 🔄 Actualizar correlativo en AgenciaDocumento
            if agencia_doc:
                agencia_doc.correlativo = next_num
                agencia_doc.save(update_fields=["correlativo"])

            out = LiquidacionDetailSerializer(liq)
            return ok(
                out.data,
                message=f"✅ Liquidación creada correctamente con correlativo {next_num} ({source}).",
                status_code=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return fail(message=f"Error al crear liquidación: {str(e)}")

    # ------------------------------------------------------
    # 🧾 OBTENER CORRELATIVO SIGUIENTE (auto incrementable)
    # ------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="next-numero")
    def next_numero(self, request):
        """
        Devuelve el correlativo actual o el siguiente número de liquidación
        según la agencia origen del usuario o la indicada por query param.
        """
        from apps.empresa.models import Agencia, AgenciaDocumento

        try:
            # 🧭 1️⃣ Determinar agencia (prioriza ?agencia_id=)
            agencia_id = request.GET.get("agencia_id") or request.session.get(
                "agencia_id"
            )
            if agencia_id:
                agencia_obj = Agencia.objects.filter(id=agencia_id).first()
            else:
                agencia_obj = Agencia.objects.filter(activo=True).first()

            if not agencia_obj:
                return fail(message="No hay agencias activas registradas.")

            # 🧾 2️⃣ Buscar documento tipo 'LI'
            agencia_doc = AgenciaDocumento.objects.filter(
                agencia=agencia_obj, documento__codigo="LI"
            ).first()

            # 3️⃣ Obtener correlativos desde doc y BD
            correlativo_doc = agencia_doc.correlativo if agencia_doc else None
            ultima_liq = (
                Liquidacion.objects.filter(agenciaOrigen=agencia_obj)
                .exclude(numDocumento__isnull=True)
                .order_by("-numDocumento")
                .first()
            )
            correlativo_db = ultima_liq.numDocumento if ultima_liq else None

            # 4️⃣ Determinar siguiente número
            if correlativo_db and (
                not correlativo_doc or correlativo_db >= correlativo_doc
            ):
                next_num = correlativo_db + 1
                source = "BD (último registro)"
            elif correlativo_doc:
                next_num = correlativo_doc + 1
                source = "AgenciaDocumento"
            else:
                next_num = 1
                source = "Fallback inicial"

            return ok(
                {"numLiquidacion": next_num},
                message=f"Correlativo obtenido desde {source} para {agencia_obj.nombre}.",
            )

        except Exception as e:
            return fail(message=f"Error al obtener correlativo: {str(e)}")

    # ------------------------------------------------------
    # 📋 LISTAR ENCOMIENDAS DISPONIBLES PARA AGREGAR A UNA LIQUIDACIÓN
    # ------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="encomiendas-disponibles")
    def encomiendas_disponibles(self, request, pk=None):
        """
        Devuelve las encomiendas que pertenecen a la agencia de origen de la liquidación,
        que aún no están agregadas a ninguna liquidación y cuyo estado es 'agenciaOrigen'.
        Similar al template liquidacion/add-encomienda.html.
        """
        try:
            liquidacion = self.get_object()

            # 🔎 Buscar encomiendas pendientes (solo de esa agenciaOrigen)
            disponibles = (
                Encomienda.objects.filter(
                    agenciaOrigen=liquidacion.agenciaOrigen,
                    estado="agenciaOrigen",
                )
                .exclude(
                    id__in=liquidacion.encomienda.all().values_list("id", flat=True)
                )
                .select_related("remite", "consignado", "agenciaDestino", "venta")
                .order_by("-venta__create")
            )

            serializer = EncomiendaListSerializer(disponibles, many=True)
            entity = serializer.data

            # 🧩 Agregamos info adicional como fechas, remite, consignado y detalle
            for item in entity:
                encomienda = disponibles.filter(id=item["id"]).first()
                if encomienda and hasattr(encomienda, "venta"):
                    item["fechaCreacion"] = (
                        encomienda.venta.create.isoformat()
                        if encomienda.venta
                        else None
                    )
                    item["detalle"] = list(
                        encomienda.venta.detallemov_set.values(
                            "descripcion", "cantidad", "valorUnitario", "subTotal"
                        )
                    )

            return ok(
                entity,
                message=f"Se encontraron {len(entity)} encomiendas disponibles para agregar.",
            )

        except Exception as e:
            return fail(message=f"Error al obtener encomiendas disponibles: {str(e)}")

    # ------------------------------------------------------
    # ➕ AGREGAR ENCOMIENDAS A UNA LIQUIDACIÓN (ya existente)
    # ------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="agregar-encomiendas")
    def agregar_encomiendas(self, request, pk=None):
        """
        Agrega una lista de encomiendas (por id) a la liquidación.
        Similar al formulario 'add-encomienda.html' original.
        """
        try:
            liquidacion = self.get_object()
            encom_ids = request.data.get("encomiendas", [])

            if not isinstance(encom_ids, list) or not encom_ids:
                return fail(
                    message="Debe enviar una lista de IDs de encomiendas válidas."
                )

            disponibles = Encomienda.objects.filter(
                id__in=encom_ids, estado="agenciaOrigen"
            )
            liquidacion.encomienda.add(*disponibles)

            return ok(
                {"added": [e.id for e in disponibles]},
                message=f"Se agregaron {len(disponibles)} encomiendas a la liquidación {liquidacion.numDocumento}.",
            )

        except Exception as e:
            return fail(message=f"Error al agregar encomiendas: {str(e)}")

    # ------------------------------------------------------
    # 🗑️ QUITAR ENCOMIENDAS DE UNA LIQUIDACIÓN
    # ------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="quitar-encomiendas")
    def quitar_encomiendas(self, request, pk=None):
        """
        Quita encomiendas seleccionadas (por id) de la liquidación.
        Similar al formulario 'sacar-encomienda.html' original.
        """
        try:
            liquidacion = self.get_object()
            encom_ids = request.data.get("encomiendas", [])

            if not isinstance(encom_ids, list) or not encom_ids:
                return fail(
                    message="Debe enviar una lista de IDs de encomiendas válidas."
                )

            liquidacion.encomienda.remove(*encom_ids)

            return ok(
                {"removed": encom_ids},
                message=f"Se quitaron {len(encom_ids)} encomiendas de la liquidación {liquidacion.numDocumento}.",
            )

        except Exception as e:
            return fail(message=f"Error al quitar encomiendas: {str(e)}")

    # ------------------------------------------------------
    # 🚚 FINALIZAR LIQUIDACIÓN
    # ------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="finalizar")
    def finalizar(self, request, pk=None):
        liquidacion = self.get_object()
        if liquidacion.finalizado:
            return fail(message="La liquidación ya fue finalizada.")

        liquidacion.finalizado = True
        liquidacion.usuario = request.user.persona
        liquidacion.encomienda.update(estado="enCamino")
        liquidacion.save()
        return ok(
            {"id": liquidacion.id, "finalizado": True},
            message="Liquidación finalizada correctamente.",
        )

    # ------------------------------------------------------
    # 🔎 DETALLE CON RECEPCIONADO_POR (detecta related_name dinámicamente)
    # ------------------------------------------------------
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Detecta automáticamente la relación según el modelo real
        recepcion = getattr(instance, "liquidacionrecepcion", None) or getattr(
            instance, "liquidacionrecepcion_set", None
        )
        if hasattr(recepcion, "first"):
            recepcion = recepcion.first()

        recepcionado_por = None
        fecha_recepcion = None
        observacion_recep = None

        if recepcion:
            usuario = getattr(recepcion, "usuario", None)
            recepcionado_por = (
                str(usuario.denominacion)
                if hasattr(usuario, "denominacion")
                else str(usuario) if usuario else None
            )
            fecha_recepcion = (
                recepcion.fecha.isoformat() if hasattr(recepcion, "fecha") else None
            )
            observacion_recep = getattr(recepcion, "observacion", None)

        data = serializer.data
        data["recepcionado_por"] = recepcionado_por
        data["fecha_recepcion"] = fecha_recepcion
        data["observacion_recep"] = observacion_recep

        return ok(data)

    # ------------------------------------------------------
    # 📦 RECEPCIÓN DE LIQUIDACIÓN
    # ------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="recepcion")
    def recepcion_liquidacion(self, request, pk=None):
        liquidacion = self.get_object()
        observacion = request.data.get("observacion", "")
        recp, created = liquidacionRecepcion.objects.get_or_create(
            liquidacion=liquidacion,
            defaults={"usuario": request.user.persona, "observacion": observacion},
        )
        liquidacion.encomienda.update(estado="agenciaDestino")

        data = {
            "id": liquidacion.id,
            "recepcion": True,
            "recepcionado_por": (
                str(recp.usuario.denominacion)
                if hasattr(recp.usuario, "denominacion")
                else str(recp.usuario)
            ),
            "fecha_recepcion": recp.fecha.isoformat(),
            "observacion_recep": recp.observacion,
        }
        return ok(data, message="Recepción registrada correctamente.")

    # ------------------------------------------------------
    # 🧾 IMPRESIÓN DETALLE (HTML)
    # ------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="print-detalle")
    def print_liquidacion_detalle(self, request, pk=None):
        from decimal import Decimal

        liq = self.get_object()
        encomiendas = liq.encomienda.all().order_by(
            "-agenciaDestino", "esContraEntrega"
        )
        suma_directa = liq.encomienda.filter(esContraEntrega=False).aggregate(
            Sum("precio")
        ).get("precio__sum") or Decimal("0")
        suma_contra_entrega = liq.encomienda.filter(esContraEntrega=True).aggregate(
            Sum("precio")
        ).get("precio__sum") or Decimal("0")

        suma_total = Decimal(suma_directa) + Decimal(suma_contra_entrega)
        comision_chofer = suma_total * Decimal("0.6")
        comision_agencia = suma_total * Decimal("0.4")

        context = {
            "liquidacion": liq,
            "encomiendas": encomiendas,
            "suma_directa": suma_directa,
            "suma_contra_entrega": suma_contra_entrega,
            "suma_total": suma_total,
            "comision_chofer": comision_chofer,
            "comision_agencia": comision_agencia,
        }

        view_mode = request.GET.get("view", "pdf").lower()
        template_name = (
            "apps/envio/liquidacion/print.html"
            if view_mode == "original"
            else "apps/envio/liquidacion/print_simplificado.html"
        )
        html = get_template(template_name).render(context)
        return HttpResponse(html, content_type="text/html")

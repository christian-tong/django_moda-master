# apps/notificaciones/api/views.py

# ----------------------------------------
# Imports principales
# ----------------------------------------
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status, views, generics
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from django.templatetags.static import static

# Modelos y serializers locales
from ..models import RegistroCumpleanos
from .serializers import RegistroCumpleanosSerializer
from apps.persona.models import PersonaNatural


# -----------------------------------------------------
# EnviarCorreoCumpleanosAPIView
# -----------------------------------------------------
class EnviarCorreoCumpleanosAPIView(views.APIView):
    """
    Endpoint para enviar correos de cumpleaños.

    Flujo:
    - Recibe `persona_id` (ID de PersonaNatural) y `correo`.
    - Opcionalmente recibe `mensaje` y `promo`.
    - Determina automáticamente el nombre de la persona.
    - Verifica si ya se envió un correo de cumpleaños a esa persona en el año actual.
    - Renderiza la plantilla HTML y envía el correo.
    - Registra el envío en la tabla `RegistroCumpleanos`.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        persona_id = request.data.get("persona_id")
        correo = request.data.get("correo")
        mensaje = request.data.get("mensaje", "")
        promo = request.data.get("promo", "")

        if not persona_id or not correo:
            return Response(
                {"error": "persona_id y correo son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------
        # Buscar PersonaNatural
        # ----------------------------------------
        try:
            persona_natural = PersonaNatural.objects.get(id=persona_id)
        except PersonaNatural.DoesNotExist:
            return Response(
                {"error": "PersonaNatural no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        persona = persona_natural.persona
        nombre = (
            request.data.get("nombre")
            or f"{persona_natural.nombres} {persona_natural.apellidoP} {persona_natural.apellidoM}"
        )

        # ----------------------------------------
        # Verificar si ya se envió en el año actual
        # ----------------------------------------
        ya_enviado = RegistroCumpleanos.objects.filter(
            persona=persona_natural, fecha_envio__year=now().year
        ).exists()

        if ya_enviado:
            return Response(
                {"message": "Ya se envió un correo de cumpleaños a esta persona hoy."},
                status=status.HTTP_200_OK,
            )

        # ----------------------------------------
        # Preparar y enviar correo
        # ----------------------------------------
        subject = f"🎉 ¡Feliz cumpleaños, {nombre}!"
        html_message = render_to_string(
            "emails/cumpleanos.html",
            {
                "nombre": nombre,
                "mensaje": mensaje,
                "promo": promo,
                "logo_url": request.build_absolute_uri(static("img/ModaLogoV3.png")),
                "globos_url": request.build_absolute_uri(static("img/globos.gif")),
            },
        )

        try:
            send_mail(
                subject,
                "",
                None,  # Usa DEFAULT_FROM_EMAIL
                [correo],
                html_message=html_message,
            )

            RegistroCumpleanos.objects.create(
                persona=persona_natural,  # ✅ SIEMPRE PersonaNatural
                correo=correo,
                mensaje=mensaje,
                promo=promo,
                enviado=True,
            )

            return Response(
                {"message": "Correo enviado correctamente."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error enviando correo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# -----------------------------------------------------
# RegistroCumpleanosListAPIView
# -----------------------------------------------------
class RegistroCumpleanosListAPIView(generics.ListAPIView):
    """
    Lista de correos de cumpleaños enviados.
    Soporta filtros:
    - ?persona_id= → filtra por PersonaNatural específica.
    - ?fecha=YYYY-MM-DD → filtra por fecha de envío.
    """

    serializer_class = RegistroCumpleanosSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = RegistroCumpleanos.objects.all().select_related("persona")

        persona_id = self.request.query_params.get("persona_id")
        fecha = self.request.query_params.get("fecha")

        if persona_id:
            qs = qs.filter(persona_id=persona_id)
        if fecha:
            qs = qs.filter(fecha_envio__date=fecha)

        return qs.order_by("-fecha_envio")

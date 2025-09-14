# apps/notificaciones/api/views.py

# ----------------------------------------
# Imports principales
# ----------------------------------------
from django.core.mail import send_mail  # Para enviar correos electrónicos
from django.template.loader import render_to_string  # Renderizar plantillas HTML
from rest_framework import status, views, generics
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.permissions import AllowAny  # Permitir acceso sin autenticación

# Modelos y serializers locales
from ..models import RegistroCumpleanos
from .serializers import RegistroCumpleanosSerializer
from apps.persona.models import Persona, PersonaNatural
from django.templatetags.static import static


# -----------------------------------------------------
# EnviarCorreoCumpleanosAPIView
# -----------------------------------------------------
class EnviarCorreoCumpleanosAPIView(views.APIView):
    """
    Endpoint para enviar correos de cumpleaños.

    Flujo:
    - Recibe `persona_id` y `correo`.
    - Opcionalmente recibe `mensaje` y `promo`.
    - Determina automáticamente el `nombre` si no es enviado:
        - Si es PersonaNatural: nombres + apellidos.
        - Si es Persona: denominacion.
    - Verifica si ya se envió un correo de cumpleaños a la persona
      en la fecha actual, evitando duplicados.
    - Renderiza la plantilla HTML en `templates/emails/cumpleanos.html`
      y envía el correo.
    - Registra el envío en la tabla `RegistroCumpleanos`.
    """

    # ⚠️ AllowAny: no requiere autenticación (puede controlarse con cookies/CSRF)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Procesa el envío de correo de cumpleaños.

        Espera JSON con:
        {
            "persona_id": int,     # requerido
            "correo": string,      # requerido
            "mensaje": string,     # opcional
            "promo": string        # opcional
        }
        """

        # ----------------------------------------
        # 1. Validar datos requeridos
        # ----------------------------------------
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
        # 2. Buscar persona (Natural o genérica)
        # ----------------------------------------
        persona_natural = None
        persona = None
        try:
            # Intentar encontrar PersonaNatural
            persona_natural = PersonaNatural.objects.get(id=persona_id)
            persona = persona_natural.persona
        except PersonaNatural.DoesNotExist:
            try:
                # Si no existe, intentar buscar en Persona
                persona = Persona.objects.get(id=persona_id)
                persona_natural = getattr(persona, "personanatural", None)
            except Persona.DoesNotExist:
                return Response(
                    {"error": "Persona no encontrada."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # ----------------------------------------
        # 3. Determinar nombre automáticamente
        # ----------------------------------------
        nombre = request.data.get("nombre") or (
            f"{persona_natural.nombres} {persona_natural.apellidoP} {persona_natural.apellidoM}"
            if persona_natural
            else persona.denominacion
        )

        # ----------------------------------------
        # 4. Verificar si ya se envió hoy
        # ----------------------------------------
        ya_enviado = RegistroCumpleanos.objects.filter(
            persona=persona_natural or persona,
            fecha_envio__date=now().date(),
        ).exists()

        if ya_enviado:
            return Response(
                {"message": "Ya se envió un correo de cumpleaños a esta persona hoy."},
                status=status.HTTP_200_OK,
            )

        # ----------------------------------------
        # 5. Preparar y enviar correo
        # ----------------------------------------
        subject = f"🎉 ¡Feliz cumpleaños, {nombre}!"

        # Renderizar plantilla HTML con contexto dinámico
        html_message = render_to_string(
            "emails/cumpleanos.html",
            {
                "nombre": nombre,
                "mensaje": mensaje,
                "promo": promo,  # promo se muestra solo si no es vacío
                "logo_url": request.build_absolute_uri(
                    static("img/ModaLogoV3.png")
                ),  # 🔥
                "globos_url": request.build_absolute_uri(
                    static("img/globos.gif")
                ),  # Globos en cabecera
            },
        )

        try:
            # Enviar correo usando configuración de Django
            send_mail(
                subject,  # asunto
                "",  # cuerpo en texto plano (vacío, solo HTML)
                None,  # remitente (usa DEFAULT_FROM_EMAIL si None)
                [correo],  # destinatarios
                html_message=html_message,
            )

            # ----------------------------------------
            # 6. Guardar registro en BD
            # ----------------------------------------
            RegistroCumpleanos.objects.create(
                persona=persona_natural or persona,
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
    - ?persona_id= → filtra por persona específica.
    - ?fecha=YYYY-MM-DD → filtra por fecha de envío.
    """

    serializer_class = RegistroCumpleanosSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Query base con select_related para optimizar
        qs = RegistroCumpleanos.objects.all().select_related("persona")

        # Filtrar por query params
        persona_id = self.request.query_params.get("persona_id")
        fecha = self.request.query_params.get("fecha")
        if persona_id:
            qs = qs.filter(persona_id=persona_id)
        if fecha:
            qs = qs.filter(fecha_envio__date=fecha)

        return qs.order_by("-fecha_envio")

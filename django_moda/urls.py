# BACKEND django_moda/urls.py
"""django_moda URL Configuration

Este archivo organiza todas las rutas principales del proyecto.
Separadas en:
- Rutas tradicionales (HTML templates con Django).
- Rutas API REST v1 (ya existentes).
- Rutas API REST v2 (nueva versión, empezando con sistema).
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Swagger
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

# Vista personalizada para errores
handler403 = "apps.sistema.views.custom_permission_denied_view"

# Configuración de Swagger/OpenAPI
schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Moda Tours API",
        default_version="1.0",
        description="Moda Tours API Documentation",
    ),
    public=True,
)

urlpatterns = [
    # ----------------------------
    # Django Admin
    # ----------------------------
    path("admin/", admin.site.urls),
    # ----------------------------
    # SISTEMA ORIGINAL (HTML templates)
    # ----------------------------
    path("persona/", include("apps.persona.urls", namespace="persona")),
    path("envio/", include("apps.envio.urls", namespace="envio")),
    path("viaje/", include("apps.viaje.urls", namespace="viaje")),
    path("tesoreria/", include("apps.caja.urls", namespace="caja")),
    path("", include("apps.web.urls", namespace="web")),  # Página pública principal
    path("sistema/", include("apps.sistema.urls", namespace="sistema")),
    path("facturacion/", include("apps.facturacion.urls", namespace="facturacion")),
    path(
        "catalogosunat/", include("apps.catalogoSunat.urls", namespace="catalogosunat")
    ),
    path("empresa/", include("apps.empresa.urls", namespace="empresa")),
    # ----------------------------
    # API REST v1 (existente, no tocar)
    # ----------------------------
    path(
        "api/v1/",
        include(
            [
                # Documentación Swagger para v1
                path(
                    "swagger/schema/",
                    schema_view.with_ui("swagger", cache_timeout=0),
                    name="swagger-schema-v1",
                ),
                path("persona/", include("apps.persona.urls", namespace="persona")),
                path("envio/", include("apps.envio.urls", namespace="envio")),
                path("viaje/", include("apps.viaje.urls", namespace="viaje")),
                path("tesoreria/", include("apps.caja.urls", namespace="caja")),
                path("sistema/", include("apps.sistema.urls", namespace="sistema")),
                path(
                    "facturacion/",
                    include("apps.facturacion.urls", namespace="facturacion"),
                ),
                path(
                    "catalogosunat/",
                    include("apps.catalogoSunat.urls", namespace="catalogosunat"),
                ),
                path("empresa/", include("apps.empresa.urls", namespace="empresa")),
            ]
        ),
    ),
    # ----------------------------
    # API REST v2 (nuevo, JSON puro para Next.js y Postman)
    # ----------------------------
    path(
        "api/v2/",
        include(
            [
                # Swagger específico para v2
                path(
                    "swagger/schema/",
                    schema_view.with_ui("swagger", cache_timeout=0),
                    name="swagger-schema-v2",
                ),
                # 🔥 Nuevas APIs v2
                path(
                    "sistema/",
                    include(
                        ("apps.sistema.api.urls", "api-sistema"),
                        namespace="api-sistema",
                    ),
                ),
                path(
                    "facturacion/",
                    include(
                        ("apps.facturacion.api.urls", "api-facturacion"),
                        namespace="api-facturacion",
                    ),
                ),
                path(
                    "envio/",
                    include(
                        ("apps.envio.api.urls", "api-envio"), namespace="api-envio"
                    ),
                ),
                path(
                    "catalogosunat/",
                    include(
                        ("apps.catalogoSunat.api.urls", "api-catalogosunat"),
                        namespace="api-catalogosunat",
                    ),
                ),
                path(
                    "empresa/",
                    include(
                        ("apps.empresa.api.urls", "api-empresa"),
                        namespace="api-empresa",
                    ),
                ),
                path(
                    "personas/",
                    include(
                        ("apps.persona.API.urls", "api-persona"),
                        namespace="api-persona",
                    ),
                ),
                path(
                    "viaje/",
                    include(
                        ("apps.viaje.API.urls", "api-viaje"),
                        namespace="api-viaje",
                    ),
                ),
                path(
                    "notificaciones/",
                    include(
                        ("apps.notificaciones.api.urls", "api-notificaciones"),
                        namespace="api-notificaciones",
                    ),
                ),
            ]
        ),
    ),
]

# ----------------------------
# Archivos estáticos y media en modo DEBUG
# ----------------------------
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

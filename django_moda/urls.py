"""django_moda URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.sistema.views import custom_permission_denied_view

# Swagger
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view


handler403 = "apps.sistema.views.custom_permission_denied_view"

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Moda Tours API",
        default_version="1.0",
        description="Moda Tours API Documentation",
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("persona/", include("apps.persona.urls", namespace="persona")),
    path("envio/", include("apps.envio.urls", namespace="envio")),
    path("viaje/", include("apps.viaje.urls", namespace="viaje")),
    path("tesoreria/", include("apps.caja.urls", namespace="caja")),
    path("", include("apps.web.urls", namespace="web")),
    path("sistema/", include("apps.sistema.urls", namespace="sistema")),
    path("facturacion/", include("apps.facturacion.urls", namespace="facturacion")),
    path(
        "catalogosunat/", include("apps.catalogoSunat.urls", namespace="catalogosunat")
    ),
    path("empresa/", include("apps.empresa.urls", namespace="empresa")),
    path(
        "api/v1/",
        include(
            [
                path(
                    "swagger/schema/",
                    schema_view.with_ui("swagger", cache_timeout=0),
                    name="swagger-schema",
                ),
                path("persona/", include("apps.persona.urls", namespace="persona")),
                path("envio/", include("apps.envio.urls", namespace="envio")),
                path("viaje/", include("apps.viaje.urls", namespace="viaje")),
                path("tesoreria/", include("apps.caja.urls", namespace="caja")),
                path("", include("apps.web.urls", namespace="web")),
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
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

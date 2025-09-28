# BACKEND apps\catalogoSunat\api\views.py

from django.db.models import Q
from rest_framework import generics, permissions
from apps.catalogoSunat.models import Ubigeo
from .serializers import UbigeoSerializer


class UbigeoListView(generics.ListAPIView):
    """
    GET: Lista de ubigeos con búsqueda opcional (?q=).
    - Permite buscar por distrito, provincia, departamento, código o id.
    - Devuelve como máximo 50 resultados.
    """

    serializer_class = UbigeoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Ubigeo.objects.all().order_by("departamento", "provincia", "distrito")
        q = self.request.GET.get("q")

        if q:
            try:
                q_int = int(q)
            except ValueError:
                q_int = None

            filtros = (
                Q(distrito__icontains=q)
                | Q(provincia__icontains=q)
                | Q(departamento__icontains=q)
                | Q(codigo__icontains=q)
            )

            if q_int is not None:
                filtros |= Q(id=q_int)

            qs = qs.filter(filtros).distinct()

        return qs[:50]

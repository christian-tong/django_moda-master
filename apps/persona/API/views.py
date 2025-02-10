from ..models import Persona, PersonaJuridica, PersonaNatural
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import (
    PersonaJuridicaSerializerAPI,
    PersonaNaturalSerializerAPI,
    PersonaSerializer,
    PersonaSerializerAPI,
)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView


class PersonaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


class PersonaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


class PersonaViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar el CRUD de personas y la búsqueda por DNI.
    """

    queryset = Persona.objects.all()
    serializer_class = PersonaSerializerAPI

    @action(detail=False, methods=["get"], url_path="buscar-por-dni")
    def buscar_por_dni(self, request):
        """
        Consulta por DNI usando query params y devuelve el id de la persona.
        """
        dni = request.query_params.get("dni", None)
        if not dni:
            return Response(
                {"error": "El parámetro 'dni' es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            persona = Persona.objects.get(numDoc=dni)
            serializer = self.get_serializer(persona)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Persona.DoesNotExist:
            return Response(
                {"error": "No se encontró ninguna persona con el DNI proporcionado."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo registro de Persona con la estructura requerida.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class PersonaNaturalAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PersonaNaturalSerializerAPI(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        personas = PersonaNatural.objects.all()
        serializer = PersonaNaturalSerializerAPI(personas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PersonaJuridicaAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PersonaJuridicaSerializerAPI(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        personas = PersonaJuridica.objects.all()
        serializer = PersonaJuridicaSerializerAPI(personas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

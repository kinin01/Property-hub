
from django.db import models
from utils.permissions import IsAdminOrPropertyManager
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import PropertySerializer, UnitSerializer
from .models import Property, Unit
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

class UnitListCreateView(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def post(self, request, *args, **kwargs):
        print("Request data:", request.data)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        print("Validated data:", serializer.validated_data)
        serializer.save()

class UnitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]



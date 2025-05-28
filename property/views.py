
from django.apps import apps
from django.db import models
from a_users import serializers
from utils.permissions import IsAdminOrPropertyManager
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.translation import gettext_lazy as _

from .serializers import PropertySerializer, UnitSerializer
from utils.pagination import CustomPagination
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

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
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]
    

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Unit.objects.all()
        # Filter units by properties where user is owner/manager
        return Unit.objects.filter(property__owner=user) | Unit.objects.filter(property__manager=user)

    def post(self, request, *args, **kwargs):
        print("Request data:", request.data)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Save the unit with validated data.
        Ensure monthly_rent and unit_type are provided.
        """
        print("Validated data:", serializer.validated_data)
        serializer.save()

class UnitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def get_queryset(self):
        """
        Restrict access to units for properties owned/managed by the user.
        """
        user = self.request.user
        if user.role == 'admin':
            return Unit.objects.all()
        return Unit.objects.filter(property__owner=user) | Unit.objects.filter(property__manager=user)

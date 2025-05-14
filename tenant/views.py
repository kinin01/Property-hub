from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Tenant
from .serializers import TenantSerializer
from utils.permissions import IsAdminOrPropertyManager
# Create your views here.

class TenantListCreateView(generics.ListCreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def create(self, request, *args, **kwargs):
        print("Create tenant request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Create tenant serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

class TenantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def update(self, request, *args, **kwargs):
        print("Update tenant request data:", request.data)
        response = super().update(request, *args, **kwargs)
        print("Update tenant response:", response.data)
        return response

    def perform_destroy(self, instance):
        if instance.unit:  # Check if the tenant has a unit
            instance.unit.is_occupied = False
            instance.unit.save()
        instance.delete()
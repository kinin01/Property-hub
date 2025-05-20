from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from a_users import serializers
from .models import Payment, Tenant, Visitor
from django.utils.translation import gettext_lazy as _
from .serializers import PaymentSerializer, TenantSerializer, VisitorSerializer
from utils.permissions import IsAdminOrPropertyManager

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from .models import Payment, Tenant
from .serializers import PaymentSerializer
import logging

logger = logging.getLogger(__name__)
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

class VisitorListCreateView(generics.ListCreateAPIView):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def create(self, request, *args, **kwargs):
        print("Create visitor request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Create visitor serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

class VisitorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPropertyManager]

    def update(self, request, *args, **kwargs):
        print("Update visitor request data:", request.data)
        response = super().update(request, *args, **kwargs)
        print("Update visitor response:", response.data)
        return response

    def perform_destroy(self, instance):
        instance.delete()

class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(
            unit__property__owner=user
        ) | Payment.objects.filter(
            unit__property__manager=user
        )

    def post(self, request, *args, **kwargs):
        logger.info(f"Payment request data: {request.data}, User: {request.user.email}, Role: {request.user.role}")
        user = self.request.user
        if user.role == 'tenant':
            if not hasattr(user, 'tenant_profile'):
                logger.error(f"Tenant user {user.email} has no tenant profile")
                raise serializers.ValidationError(_('User does not have a tenant profile'))
            if request.data.get('tenant') != user.tenant_profile.id:
                logger.error(f"Tenant {user.email} attempted to create payment for another tenant")
                raise serializers.ValidationError(_('Tenants can only create payments for themselves'))
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        logger.info(f"Validated payment data: {serializer.validated_data}")
        try:
            serializer.save()
        except Exception as e:
            logger.error(f"Error saving payment: {str(e)}")
            raise serializers.ValidationError(_('Failed to create payment: {}').format(str(e)))

class PaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Restrict access to payments based on user role.
        - Tenants: Only their own payments.
        - Admins/Property Managers: Payments for their properties.
        """
        user = self.request.user
        if user.role == 'tenant':
            return Payment.objects.filter(tenant__user=user)
        elif user.role in ['admin', 'property_manager']:
            return Payment.objects.filter(
                unit__property__owner=user
            ) | Payment.objects.filter(
                unit__property__manager=user
            )
        return Payment.objects.none()

    def perform_update(self, serializer):
        """
        Ensure tenants can only update their own payments.
        Validate amount_due against unit's monthly_rent.
        """
        user = self.request.user
        instance = self.get_object()
        if user.role == 'tenant' and instance.tenant.user != user:
            raise serializers.ValidationError(_('Tenants can only update their own payments'))
        unit = serializer.validated_data.get('unit', instance.unit)
        amount_due = serializer.validated_data.get('amount_due', instance.amount_due)
        if amount_due != unit.monthly_rent:
            raise serializers.ValidationError(
                _('Amount due must match the unit\'s monthly rent: {}').format(unit.monthly_rent)
            )
        serializer.save()

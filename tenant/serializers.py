from django.db import models
from rest_framework import serializers
from django.db import IntegrityError
from a_users.models import CustomUser
from property.models import Unit
from tenant.models import Payment, Tenant, Visitor
from django.utils.translation import gettext_lazy as _
from .models import Payment, Tenant, Unit
import re

from rest_framework import serializers
from .models import Visitor
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class TenantSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(source='user.email')
    user = serializers.SerializerMethodField()
    # user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), allow_null=True)

    class Meta:
        model = Tenant
        fields = ['id', 'user', 'unit', 'lease_start_date', 'lease_end_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'phone_number': obj.user.phone_number
        }

    def validate(self, data):
        unit = data.get('unit')
        instance = self.instance
        if unit and instance and unit != instance.unit and unit.is_occupied:
            raise serializers.ValidationError({"unit": "This unit is already occupied."})
        if self.context['request'].method == 'POST':
            user_data = self.context['request'].data.get('user')
            if not user_data or not all(key in user_data for key in ['username', 'email', 'password']):
                raise serializers.ValidationError({"user": "User data with username, email, and password is required."})
        return data

    def create(self, validated_data):
        user_data = self.context['request'].data.get('user', {})
        try:
            user = CustomUser.objects.create_user(
                email=user_data.get('email'),
                username=user_data.get('username'),
                password=user_data.get('password'),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                phone_number=user_data.get('phone_number', '') or None,
                role='tenant'
            )
        except IntegrityError as e:
            if 'email' in str(e):
                raise serializers.ValidationError({"email": "A user with this email already exists."})
            if 'username' in str(e):
                raise serializers.ValidationError({"username": "A user with this username already exists."})
            if 'phone_number' in str(e):
                raise serializers.ValidationError({"phone_number": "A user with this phone number already exists."})
            raise serializers.ValidationError({"non_field_errors": "Failed to create user due to a database error."})

        tenant = Tenant.objects.create(
            user=user,
            unit=validated_data.get('unit'),
            lease_start_date=validated_data.get('lease_start_date'),
            lease_end_date=validated_data.get('lease_end_date')
        )

        if tenant.unit:
            tenant.unit.is_occupied = True
            tenant.unit.save()
        return tenant

    def update(self, instance, validated_data):
        old_unit = instance.unit
        unit = validated_data.get('unit')
        instance.unit = unit
        instance.lease_start_date = validated_data.get('lease_start_date', instance.lease_start_date)
        instance.lease_end_date = validated_data.get('lease_end_date', instance.lease_end_date)
        instance.save()
        if old_unit and old_unit != unit:
            old_unit.is_occupied = False
            old_unit.save()
        if unit and unit != old_unit:
            unit.is_occupied = True
            unit.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.unit:
            representation['unit'] = {
                'id': instance.unit.id,
                'unit_number': instance.unit.unit_number,
                'property': {
                    'id': instance.unit.property.id,
                    'name': instance.unit.property.name
                } if instance.unit.property else None
            }
        else:
            representation['unit'] = None
        return representation


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        tenant_name = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all(), allow_null=True)
        fields = ['id', 'tenant', 'unit', 'visitor_name', 'email']
        read_only_fields = ['id', 'tenant', 'tenant_name']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        # Validate tenant-unit association for non-null unit
        if data.get('tenant') and data.get('unit'):
            if data['tenant'].unit != data['unit']:
                raise serializers.ValidationError("The selected tenant is not associated with this unit.")

        # Tenant-specific validation
        if user and user.role == 'tenant':
            # Allow unit to be null or match user's unit
            if data.get('unit') and (hasattr(user, 'unit') and user.unit and data.get('unit') != user.unit):
                raise serializers.ValidationError("You can only book visitors for your own unit.")
            # Tenants can only set themselves as the tenant
            if data.get('tenant') and data['tenant'] != user:
                raise serializers.ValidationError("You can only book visitors as yourself.")

        return data

    def create(self, validated_data):
        visitor = Visitor.objects.create(**validated_data)
        return visitor

class PaymentSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(queryset=Tenant.objects.all())
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())

    class Meta:
        model = Payment
        fields = [
            'id', 'tenant', 'unit', 'amount_due', 'amount_paid', 'payment_method',
            'payment_status', 'transaction_id', 'billing_period', 'payment_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'payment_date']

    def validate_tenant(self, value):
        if not Tenant.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(_('Invalid tenant ID'))
        return value

    def validate_unit(self, value):
        if not Unit.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(_('Invalid unit ID'))
        return value

    def validate_billing_period(self, value):
        if not re.match(r'^\d{4}-\d{2}$', value):
            raise serializers.ValidationError(_('Billing period must be in YYYY-MM format'))
        try:
            year, month = map(int, value.split('-'))
            if not (1 <= month <= 12):
                raise serializers.ValidationError(_('Invalid month in billing period'))
        except ValueError:
            raise serializers.ValidationError(_('Billing period must be in YYYY-MM format'))
        return value

    def validate_payment_method(self, value):
        if value not in dict(Payment.PAYMENT_METHODS).keys():
            raise serializers.ValidationError(_('Invalid payment method'))
        return value

    def validate_payment_status(self, value):
        if value not in dict(Payment.PAYMENT_STATUSES).keys():
            raise serializers.ValidationError(_('Invalid payment status'))
        return value

    def validate_amount_due(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Amount due cannot be negative'))
        return value

    def validate_amount_paid(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Amount paid cannot be negative'))
        return value

    def validate(self, data):
        unit = data.get('unit')
        amount_due = data.get('amount_due')
        if unit and amount_due is not None:
            if amount_due != unit.monthly_rent:
                raise serializers.ValidationError(
                    _('Amount due must match the unit\'s monthly rent: {}').format(unit.monthly_rent)
                )
        return data
    
    
from django.db import models
from rest_framework import serializers
from django.db import IntegrityError
from a_users.models import CustomUser
from property.models import Unit
from tenant.models import Tenant
class TenantSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
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
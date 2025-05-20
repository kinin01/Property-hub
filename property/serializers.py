
from django.apps import apps
from django.db import models
from a_users.models import CustomUser
from property.models import Unit
from .models import  Property
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
class PropertySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Property
        fields = ['id','name', 'address', 'description', 'owner', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['created_at', 'updated_at']

    def validate_owner(self, value):
        if value.role not in ['landlord', 'property_manager', 'admin']:
            raise serializers.ValidationError("Owner must be a landlord, property manager, or admin.")
        return value
# Add UnitSerializer

class UnitSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = Unit
        fields = [
            'id',
            'property',
            'unit_number',
            'unit_type',
            'monthly_rent',
            'description',
            'is_occupied',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_occupied']

    def validate_unit_type(self, value):
        if value not in dict(Unit.UNIT_TYPES).keys():
            raise serializers.ValidationError(_('Invalid unit type. Choices are: {}').format(
                ', '.join([f'{k} ({v})' for k, v in Unit.UNIT_TYPES])
            ))
        return value

    def validate_monthly_rent(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Monthly rent cannot be negative.'))
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['property'] = {
            'id': instance.property.id,
            'name': instance.property.name
        }
        representation['unit_type_display'] = instance.get_unit_type_display()
        return representation

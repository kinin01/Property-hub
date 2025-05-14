
from django.db import models
from a_users.models import CustomUser
from property.models import Unit
from .models import Property
from rest_framework import serializers
class PropertySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'description', 'owner', 'created_at', 'updated_at', 'is_active']
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
        fields = ['id', 'property', 'unit_number', 'description', 'is_occupied', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'is_occupied']  # is_occupied is read-only to prevent manual changes

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['property'] = {'id': instance.property.id, 'name': instance.property.name}
        return representation
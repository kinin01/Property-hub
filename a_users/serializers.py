from django.db import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

from property.serializers import UnitSerializer
from tenant.models import Payment, Tenant
from tenant.serializers import TenantSerializer
from .models import CustomUser

from django.contrib.auth import get_user_model


class CustomUserSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'unit']
    
    def get_unit(self, obj):
        """Get unit data through tenant relationship with optimized query"""
        if obj.role == 'tenant':
            try:
                tenant = Tenant.objects.select_related('unit__property').get(user=obj)
                if tenant.unit:
                    return {
                        'id': tenant.unit.id,
                        'unit_number': tenant.unit.unit_number,
                        'property': {
                            'id': tenant.unit.property.id,
                            'name': tenant.unit.property.name
                        } if tenant.unit.property else None
                    }
            except Tenant.DoesNotExist:
                pass
        return None
    @property
    def tenant_unit(self):
        """Get the unit for tenant users"""
        if self.role == 'tenant':
            try:
                tenant_profile = Tenant.objects.select_related('unit').get(user=self)
                return tenant_profile.unit
            except Tenant.DoesNotExist:
                return None
        return None
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            raise serializers.ValidationError("Identifier and password are required.")

        user = None

        # Try to find user by email, username, or phone number
        UserModel = get_user_model()
        
        if '@' in identifier:
            try:
                user = UserModel.objects.get(email=identifier)
            except UserModel.DoesNotExist:
                pass
        elif identifier.isdigit() and len(identifier) == 10: 
            try:
                user = UserModel.objects.get(phone_number=identifier)
            except UserModel.DoesNotExist:
                pass
        else:
            try:
                user = UserModel.objects.get(username=identifier)
            except UserModel.DoesNotExist:
                pass

        if user and user.check_password(password):
            data['user'] = user
        else:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, default='Admin')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role', 'phone_number']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', 'tenant')
        )
        return user


    
class PaymentSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()
    unit = UnitSerializer()
    class Meta:
        model = Payment
        fields = ['id', 'tenant', 'unit', 'amount_due', 'amount_paid', 'billing_period']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['amount_due'] = float(instance.amount_due) if instance.amount_due is not None else 0.0
        representation['amount_paid'] = float(instance.amount_paid) if instance.amount_paid is not None else 0.0
        return representation
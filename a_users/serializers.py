from django.db import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import CustomUser, Property, Tenant, Unit

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number']

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
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()

        # Try to find user by email, username, or phone number
        if '@' in identifier:
            try:
                user = UserModel.objects.get(email=identifier)
            except UserModel.DoesNotExist:
                pass
        elif identifier.isdigit() and len(identifier) == 10:  # Assuming 10-digit phone number
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
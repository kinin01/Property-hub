from rest_framework import permissions
from property.models import Unit
from tenant.models import Tenant

# class IsAdminOrPropertyManager(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role in ['property_manager', 'admin']
    

#     def has_object_permission(self, request, view, obj):
#         if request.user.role == 'admin':
#             return True
#         if request.user.role == 'property_manager':
#             if isinstance(obj, Unit):
#                 return request.user == obj.property.owner
#             if isinstance(obj, Tenant) and obj.unit:
#                 return request.user == obj.unit.property.owner
#         return False

from rest_framework import permissions
from django.contrib.auth import get_user_model
from tenant.models import Unit, Tenant, Visitor
User = get_user_model()

class IsAdminOrPropertyManager(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow authenticated users with valid roles
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'property_manager', 'tenant']
        )

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role == 'admin':
            return True
        # Property managers can access if they own the property
        if request.user.role == 'property_manager':
            if isinstance(obj, Unit):
                return request.user == obj.property.owner
            if isinstance(obj, Tenant) and obj.unit:
                return request.user == obj.unit.property.owner
            if isinstance(obj, Visitor) and obj.unit:
                return request.user == obj.unit.property.owner
        # Tenants can only access their own visitors
        if request.user.role == 'tenant':
            if isinstance(obj, Visitor):
                return obj.tenant == request.user
        return False
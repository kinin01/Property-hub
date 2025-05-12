from rest_framework import permissions
from a_users.models import Property, Tenant, Unit

class IsAdminOrPropertyManager(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow authenticated users with 'admin' or 'property_manager' roles to create/list
        return request.user.is_authenticated and request.user.role in ['property_manager', 'admin']

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role == 'admin':
            return True
        # Property managers can manage objects if they own the related property
        if request.user.role == 'property_manager':
            if isinstance(obj, Unit):
                return request.user == obj.property.owner
            if isinstance(obj, Tenant) and obj.unit:
                return request.user == obj.unit.property.owner
        return False
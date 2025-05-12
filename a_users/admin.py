from django.contrib import admin
from .models import CustomUser, Property, Tenant, Unit

admin.site.register(CustomUser)
admin.site.register(Property)
admin.site.register(Tenant)
admin.site.register(Unit)
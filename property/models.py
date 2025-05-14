from django.db import models
from a_users.models import CustomUser
from django.utils.translation import gettext_lazy as _

class Property(models.Model):
    name = models.CharField(_('property name'), max_length=255)
    address = models.TextField(_('address'))
    description = models.TextField(_('description'), blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('property')
        verbose_name_plural = _('properties')

    def __str__(self):
        return self.name
    

class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(_('unit number'), max_length=50) 
    description = models.TextField(_('description'), blank=True)
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')
        unique_together = ('property', 'unit_number')  # Ensure unique unit numbers per property

    def __str__(self):
        return f"{self.unit_number} - {self.property.name}"
from datetime import timezone
from django.db import models
from a_users.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
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
    
# Updated Unit Model
class Unit(models.Model):
    UNIT_TYPES = (
        ('1B', _('1 Bedroom')),
        ('2B', _('2 Bedroom')),
        ('3B', _('3 Bedroom')),
        ('ST', _('Studio')),
        ('OT', _('Other')),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name=_('property')
    )
    unit_number = models.CharField(_('unit number'), max_length=50)
    unit_type = models.CharField(
        _('unit type'),
        max_length=2,
        choices=UNIT_TYPES,
        default='OT',
        help_text=_('Type of unit, e.g., 1 Bedroom, 2 Bedroom')
    )
    monthly_rent = models.DecimalField(
        _('monthly rent'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Monthly rent in Ksh, e.g., 10000.00 for 1B')
    )
    description = models.TextField(_('description'), blank=True)
    is_occupied = models.BooleanField(_('is occupied'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')
        unique_together = ('property', 'unit_number')
        indexes = [
            models.Index(fields=['property', 'unit_number']),
            models.Index(fields=['unit_type']),
        ]

    def __str__(self):
        return f"{self.unit_number} ({self.get_unit_type_display()}) - {self.property.name}"
    

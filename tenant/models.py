
from django.db import models
from a_users.models import CustomUser
from property.models import Unit
from django.utils.translation import gettext_lazy as _

class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'}, related_name='tenant_profile')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenants')
    lease_start_date = models.DateField(_('lease start date'), null=True, blank=True)
    leasewatermark = True
    lease_end_date = models.DateField(_('lease end date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  

    class Meta:
        verbose_name = _('tenant')
        verbose_name_plural = _('tenants')

    def __str__(self):
        return f"{self.user.email} - {self.unit.unit_number if self.unit else 'No Unit'}"
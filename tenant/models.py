from django.utils import timezone
from django.db import models
from a_users.models import CustomUser
from property.models import Unit
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

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

class Visitor(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        related_name='visitors',
        null=True,
        blank=True,
        verbose_name=_('tenant')
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='visitors',
        verbose_name=_('unit')
    )
    visitor_name = models.CharField(_('visitor name'), max_length=255)
    email = models.EmailField(_('email address'), blank=True, null=True)

    class Meta:
        verbose_name = _('visitor')
        verbose_name_plural = _('visitors')

    def __str__(self):
        return f"{self.visitor_name} (ID: {self.id})"
    
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('CASH', _('Cash')),
        ('MPESA', _('M-Pesa')),
        ('CARD', _('Card')),
    )
    PAYMENT_STATUSES = (
        ('PENDING', _('Pending')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
    )

  
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('tenant')
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('unit')
    )
    amount_due = models.DecimalField(
        _('amount due'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Total amount due for the billing period')
    )
    amount_paid = models.DecimalField(
        _('amount paid'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Amount paid by the tenant')
    )
    payment_method = models.CharField(
        _('payment method'),
        max_length=10,
        choices=PAYMENT_METHODS,
        default='CASH'
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=10,
        choices=PAYMENT_STATUSES,
        default='PENDING'
    )
    transaction_id = models.CharField(
        _('transaction ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Transaction ID from payment provider, e.g., M-Pesa code')
    )
    billing_period = models.CharField(
        _('billing period'),
        max_length=7,
        help_text=_('Billing period in YYYY-MM format, e.g., 2025-05'),
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{2}$',
                message=_('Billing period must be in YYYY-MM format')
            )
        ]
    )
    payment_date = models.DateTimeField(
        _('payment date'),
        null=True,
        blank=True,
        help_text=_('Date of payment completion')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        indexes = [
            models.Index(fields=['tenant', 'billing_period']),
            models.Index(fields=['unit', 'billing_period']),
            models.Index(fields=['payment_status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_due__gte=0),
                name='amount_due_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(amount_paid__gte=0),
                name='amount_paid_non_negative'
            ),
        ]

    def __str__(self):
        Tenant = Tenant
        tenant_email = self.tenant.user.email if self.tenant and hasattr(self.tenant, 'user') else 'Unknown'
        return f"Payment {self.id} - {tenant_email} for {self.billing_period}"
    
    

    def save(self, *args, **kwargs):
        if self.payment_status == 'COMPLETED' and not self.payment_date:
            self.payment_date = timezone.now()
        elif self.payment_status != 'COMPLETED':
            self.payment_date = None
        super().save(*args, **kwargs)